"""Scene CRUD + Run lifecycle — data-driven across every node class."""
import pytest

from tests.base.base_test import BaseTest
from tests.data.test_data import TestData

_VALUES, _IDS = TestData.scene_lifecycle()


class TestSceneLifecycle(BaseTest):

    @pytest.mark.smoke
    @pytest.mark.parametrize("test_id, node_type, group, scene_id, s_value", _VALUES, ids=_IDS)
    def test_create_run_delete(self, test_id, node_type, group, scene_id, s_value, node_ids):
        scenes = self.scene_page()
        node = node_ids[node_type]

        created = scenes.create(scene_id, group, node, s_value)
        assert created == {"cmd": 1, "sid": scene_id, "rc": 0}

        ran = scenes.run(scene_id)
        assert ran["rc"] == 0 and ran["sid"] == scene_id

        deleted = scenes.delete(scene_id)
        assert deleted["rc"] == 0 and deleted["sid"] == scene_id

    @pytest.mark.regression
    def test_run_unknown_scene_fails(self):
        """A scene that was never created cannot be run (rc != 0)."""
        assert self.scene_page().run(999999)["rc"] != 0

    @pytest.mark.regression
    def test_edit_scene_swaps_node(self, node_ids):
        """Create a 2G scene, edit it to add a fan dimmer and drop the 2G node."""
        scenes = self.scene_page()
        sid = 210
        scenes.create(sid, "TP", node_ids["2g"], 9)

        edited = scenes.edit(
            sid,
            add={"FD": [{"id": node_ids["fd"], "s": [6, 1]}]},
            delete=[node_ids["2g"]],
        )
        assert edited == {"cmd": 2, "sid": sid, "rc": 0}
        assert scenes.run(sid)["rc"] == 0
        assert scenes.delete(sid)["rc"] == 0
