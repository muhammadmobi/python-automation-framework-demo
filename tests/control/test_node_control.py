"""Direct node control via the device shadow, plus device detect."""
import pytest

from tests.base.base_test import BaseTest
from tests.data.test_data import TestData

_ON, _ON_IDS = TestData.turn_on()
_OFF, _OFF_IDS = TestData.turn_off()


class TestNodeControl(BaseTest):

    @pytest.mark.smoke
    @pytest.mark.parametrize("test_id, node_type, desired, applied", _ON, ids=_ON_IDS)
    def test_turn_on_node(self, test_id, node_type, desired, applied, shadow_id):
        node = shadow_id(node_type)
        response = self.control_page().set_switch(node, desired)
        assert response["state"]["reported"][node]["s"][1] == applied

    @pytest.mark.regression
    @pytest.mark.parametrize("test_id, node_type, desired, applied", _OFF, ids=_OFF_IDS)
    def test_turn_off_node(self, test_id, node_type, desired, applied, shadow_id):
        node = shadow_id(node_type)
        response = self.control_page().set_switch(node, desired)
        assert response["state"]["reported"][node]["s"][1] == applied

    @pytest.mark.regression
    @pytest.mark.parametrize("node_type, node_label", [("4g", "4G"), ("3g", "3G"), ("fd", "FD")])
    def test_detect_is_fire_and_forget(self, node_type, node_label, node_ids):
        """Detect publishes with no response; the offline hub records the broadcast."""
        page = self.control_page()
        page.detect(node_ids[node_type], node_label)
        if page.hub is not None:
            assert {"id": node_ids[node_type], "t": node_label} in page.hub.state.detected
