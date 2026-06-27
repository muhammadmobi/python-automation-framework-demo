# Python Automation Framework — Demo (Virtual MHub)

[![CI](https://github.com/your-org/python-automation-framework-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/python-automation-framework-demo/actions/workflows/ci.yml)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-style **pytest** automation framework for an **MQTT / IoT** product —
the *MHub MasterHub* building-automation gateway. It follows the **same
Page Object Model architecture** as its sibling demos
(`appium-automation-framework-demo`, `cypress-automation-framework-demo`):
`ConfigReader → DriverFactory/DriverManager → BasePage → Page Objects →
BaseTest + Listeners + TestData + smoke/regression suites`.

To keep it runnable by anyone with **zero setup**, the repo ships its **own
target**: a self-contained **virtual MasterHub** that speaks the exact MQTT
protocol over an in-process broker. The whole suite runs offline, in CI, with
**no AWS IoT endpoint and no certificates**.

> The Python counterpart of a real hardware E2E suite (`Mhub_TestScripts`) that
> drives a physical ESP32 hub through AWS IoT Core. Here the hardware + cloud are
> replaced by a bundled simulator so the protocol, framework design and tests can
> be showcased end-to-end on a laptop.

---

## Framework parity with the sibling demos

The Appium demo's UI-automation building blocks map 1:1 onto MQTT here:

| Shared framework concept | Appium (UI) | This demo (MQTT) |
| --- | --- | --- |
| **ConfigReader** | `config.properties` + `-D` overrides | `resources/config.properties` + env overrides |
| **DriverFactory** | builds `AndroidDriver` | builds the MQTT `HubSession` (in-proc or AWS) |
| **DriverManager** | `ThreadLocal<AndroidDriver>` | `threading.local` `HubSession` |
| **BasePage** | waits + `tap`/`type`/`textOf` | `publish` / `request` / `wait_for_response` |
| **Page Objects** | `MqttPage`, `BlePage`, … (one per screen) | `ScenePage`, `NodeControlPage`, `ConfigurationPage`, `AutomationPage` (one per domain) |
| **BaseTest** | `@Before/@After` driver lifecycle | `driver` session fixture + page accessors |
| **TestListener** | log + screenshot on failure | log + **hub-state dump** on failure |
| **TestData** | TestNG `@DataProvider` | `TestData` providers + `parametrize` |
| **Suites** | `smoke.xml` / `regression.xml` | `resources/suites/smoke.ini` / `regression.ini` |

---

## Project structure

```
python-automation-framework-demo/
├── gateway/                    # ← the framework (Page Object Model)
│   ├── config/   ConfigReader              # externalised, env-overridable config
│   ├── driver/   DriverFactory             # builds the MQTT HubSession from config
│   │             DriverManager             # thread-local session (parallel-safe)
│   │             transport.py · mqtt_client.py · session.py
│   ├── base/     BasePage                  # publish/request/wait actions
│   ├── pages/    ScenePage · NodeControlPage · ConfigurationPage · AutomationPage
│   └── protocol/ messages.py · topics.py   # the MHub wire format (the "locator" layer)
├── simulator/                  # ← the bundled target under test (virtual hub)
│   ├── broker.py · virtual_hub.py · state.py
│   └── handlers/ scene · shadow · config · automation · detect
├── tests/
│   ├── base/        BaseTest               # driver lifecycle + page accessors
│   ├── listeners/   listener.py            # pass/fail logging + failure artifact
│   ├── data/        TestData               # data providers
│   ├── conftest.py                         # fixtures + listener hook wiring
│   └── scene/  control/  config/  automation/
├── resources/
│   ├── config.properties                   # framework settings (placeholders)
│   ├── config.json                         # protocol: topics / node ids / commands
│   └── suites/  smoke.ini  regression.ini
├── pytest.ini · setup.cfg · pyproject.toml
├── .github/workflows/ci.yml                # lint-and-format → test → report
└── framework-documentation.md              # full design write-up
```

---

## Getting started

```bash
python -m venv .venv && . .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest                                           # full (regression) suite, offline
pytest -c resources/suites/smoke.ini             # smoke suite only
pytest --html=report.html --self-contained-html  # with an HTML report
```

No broker, no AWS account, no certificates required — the in-process simulator is
the default target.

---

## The protocol at a glance

The hub exchanges JSON over five MQTT domains. Page Objects publish to the
`…/mn/{id}/…` (device-bound) topics; the hub replies on the `…/cloud/{id}/…`
(and shadow `accepted`) topics.

| Domain | Page Object | Publish topic | Message → Response |
| --- | --- | --- | --- |
| **Scene** | `ScenePage` | `…/mn/{id}/scene` | `{cmd,sid,devices}` → `{cmd,sid,rc:0}` |
| **Shadow** | `NodeControlPage` | `$aws/things/{id}/shadow/update` | `{state:{desired:{node:{s}}}}` → `{state:{reported:…}}` |
| **Config** | `ConfigurationPage` | `…/mn/{id}/device/configure` | `{id,t,bl/th/ol,d_id}` → echo `{…,rc:0}` |
| **Detect** | `NodeControlPage` | `…/mn/{id}/device/detect` | `{id,t}` (fire-and-forget) |
| **Automation** | `AutomationPage` | `…/mn/{id}/automation` | `{aid,sid,md,cmd,time,at}` → `{aid,sid,rc:0,devices}` |

---

## Test inventory

| Suite | IDs | Covers |
| --- | --- | --- |
| `tests/scene/` | `MHUB-SCENE-*` | Create → run → delete across 4G/3G/2G/1G/PP/SR/SP; edit (node swap); negative run |
| `tests/control/` | `MHUB-CTRL-*` | Shadow on/off per node, applied-state assertions, fire-and-forget detect |
| `tests/config/` | `MHUB-CFG-*` | Backlight enable/disable, touch threshold, fan-dimmer on-state level |
| `tests/automation/` | `MHUB-AUTO-*` | Ordered time-window create → edit → delete with per-device return codes |

---

## Pointing it at real hardware (AWS IoT Core)

The framework is transport-agnostic — the same Page Objects and tests run against
a physical hub by flipping one config value:

```bash
export MHUB_TRANSPORT=aws
export DEVICE_ID=your-device-thing-name
export MQTT_ENDPOINT=your-endpoint.iot.eu-west-1.amazonaws.com
export MQTT_ROOTCAPATH=Credentials/root-ca.pem
export MQTT_PRIVATEKEYPATH=Credentials/private.key
export MQTT_CERTPATH=Credentials/certificate.pem
pip install AWSIoTPythonSDK
pytest
```

Every key in `resources/config.properties` is overridable by the matching env var
(dots → underscores, upper-cased). Keep real certificates out of source control —
`Credentials/` and `*.pem`/`*.key` are git-ignored.

---

## Security & secrets

This is a **showcase repository in working condition** — it contains **no real
secrets, credentials, certificates, endpoints, database IDs or device names**.
Everything is a deliberately fake placeholder:

- **No certificates / keys** are committed; `Credentials/`, `*.pem` and `*.key`
  are git-ignored, and none are required for the default offline run.
- **Topics** use a neutral `mhub/demo/...` namespace; **database UUIDs** are
  obvious zero-filled placeholders (`00000000-0000-4000-8000-0000000000NN`);
  **device id** is `MHUB-DEMO-DEVICE-001`; the **AWS endpoint** is the literal
  string `your-endpoint.iot.eu-west-1.amazonaws.com`.
- The bundled virtual hub means the full suite runs **fully offline** with no
  external connection, so running this repo cannot reach, affect or leak anything
  from any real system.

Supply real values only at runtime via environment variables or CI secrets —
never commit them.

---

## License

[MIT](LICENSE)
