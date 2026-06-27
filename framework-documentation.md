# Framework Documentation

This document explains the **design** of the demo: the framework it follows, how
a message flows through the layers, and how to extend it.

## 1. Goals

1. **Follow the house framework.** Use the exact Page Object Model architecture of
   the sibling demos (`appium-automation-framework-demo`,
   `cypress-automation-framework-demo`) — same layering, same vocabulary
   (`ConfigReader`, `DriverFactory`, `DriverManager`, `BasePage`, Page Objects,
   `BaseTest`, `TestListener`, `TestData`, smoke/regression suites).
2. **Mirror the production protocol** (`Mhub_TestScripts`) faithfully — same
   topics, JSON shapes and return-code semantics — so it is a drop-in once
   pointed at a real endpoint.
3. **Stay deterministic and offline** — no network, no sleeps, no flake.

## 2. Page Object Model — the layers

```
 tests/ (BaseTest)         intent only — "create a scene, assert rc==0"
      │ uses
 gateway/pages/            Page Objects: ScenePage, NodeControlPage,
      │ extends            ConfigurationPage, AutomationPage
 gateway/base/BasePage     reusable actions: publish / request / wait_for_response
      │ pulls
 gateway/driver/           DriverManager (thread-local HubSession)
      │ built by           DriverFactory  ◄── ConfigReader (resources/config.properties)
 gateway/driver/transport  InProcessTransport  |  AwsIotTransport
      │
 simulator/  (offline)     InProcessBroker ─► VirtualHub ─► handlers ─► HubState
```

Every Appium UI concept has a direct MQTT counterpart:

| Appium (UI) | This demo (MQTT) | File |
| --- | --- | --- |
| `ConfigReader` (`config.properties`, `-D` overrides) | `ConfigReader` (`config.properties`, env overrides) | `gateway/config/config_reader.py` |
| `DriverFactory` → `AndroidDriver` | `DriverFactory` → `HubSession` | `gateway/driver/driver_factory.py` |
| `DriverManager` `ThreadLocal` | `DriverManager` `threading.local` | `gateway/driver/driver_manager.py` |
| `BasePage` waits + `tap`/`type` | `BasePage` `publish`/`request`/`wait` | `gateway/base/base_page.py` |
| `MqttPage`, `BlePage` … | `ScenePage`, `NodeControlPage` … | `gateway/pages/` |
| `BaseTest` `@Before/@After` | `BaseTest` + `driver` fixture | `tests/base/base_test.py` |
| `TestListener` (screenshot on fail) | listener (hub-state dump on fail) | `tests/listeners/listener.py` |
| `TestData` `@DataProvider` | `TestData` providers | `tests/data/test_data.py` |
| `smoke.xml` / `regression.xml` | `smoke.ini` / `regression.ini` | `resources/suites/` |

A topic-scheme change touches `protocol/topics.py`; a payload change touches
`protocol/messages.py`; a node-set change touches `TestData` / `config.json`.

## 3. The target under test (`simulator/`)

Like the Cypress demo ships an `app/` + `mock-api/`, this repo ships a **virtual
MasterHub** so the suite has a real target offline. `VirtualHub` subscribes to the
device-bound topics, routes each message to a domain handler
(`handlers/scene.py`, `shadow.py`, `config.py`, `automation.py`, `detect.py`),
mutates `HubState`, and publishes the response on the matching cloud topic — the
same wiring a real hub performs against AWS IoT Core, but in-process and
deterministic.

The boundary between framework and target is the `Transport` interface — the same
seam the real system has between the device and AWS IoT Core. Set
`MHUB_TRANSPORT=aws` and the simulator is simply not constructed.

## 4. Message lifecycle (worked example)

`self.scene_page().create(101, "TP", 7, 1)`:

1. `ScenePage.create` → `protocol.messages.create_scene` builds
   `{"cmd":1,"sid":101,"devices":{"TP":[{"id":7,"s":1}]}}`.
2. `BasePage.request` resolves the `scene` publish topic and calls
   `MqttClient.request`, which publishes and blocks on the response queue.
3. `InProcessBroker.publish` synchronously invokes `VirtualHub._on_message`.
4. The hub calls `handlers.scene.handle`, which records the scene in
   `HubState.scenes` and returns `{"cmd":1,"sid":101,"rc":0}`.
5. The hub publishes that on the `cloud/.../scene` topic; the broker delivers it to
   `MqttClient._on_scene`, which enqueues it.
6. `request()` pops the response and returns it to the Page Object → test.

All within one call stack — no waiting, fully deterministic.

## 5. State & return-code fidelity

`HubState` lets the simulator return *meaningful* results instead of a blanket
`rc:0`:

* Running/deleting a scene or automation that was never created → `rc != 0`
  (`tests/scene/...test_run_unknown_scene_fails`).
* Shadow updates persist the applied switch value and report it back (`s[1]`).
* Config writes persist per-node backlight/threshold/on-state level.

## 6. Driver lifecycle & isolation

The MHub "device under test" is **long-lived** — like real hardware it persists
across the session (`driver` is a session-scoped fixture). The autouse `_isolate`
fixture drains the response queue between tests so ordering quirks never leak.
This also lets the ordered automation chain (create → edit → delete, via
`pytest-dependency`) share one device, exactly as on hardware. The thread-local
`DriverManager` keeps the design parallel-safe for future `pytest-xdist` runs.

## 7. Extending the framework

**Add a command** (e.g. scene "duplicate"):
1. Builder in `gateway/protocol/messages.py`.
2. Method on the relevant Page Object in `gateway/pages/`.
3. Handle it in the matching `simulator/handlers/*.py` (+ `HubState` if stateful).
4. Spec + `TestData` row under `tests/`.

**Add a node type:** id/suffix in `resources/config.json` + `NODE_SUFFIXES`
(`tests/data/test_data.py`), then a data row.

**Run against hardware:** `MHUB_TRANSPORT=aws` + the `MQTT_*` env vars.

## 8. CI / quality gates

`.github/workflows/ci.yml` runs `lint-and-format` (flake8 + black) as a gate
before `test`, which runs the offline suite and uploads an HTML report artifact —
the production "quality gate → test → report" shape.
