"""Device configuration — backlight, touch threshold, on-state level."""
import pytest

from tests.base.base_test import BaseTest
from tests.data.test_data import TestData, DB_ID_KEYS

_BL, _BL_IDS = TestData.backlight()
_TH, _TH_IDS = TestData.thresholds()


def _db_id(node_ids, node_type):
    return node_ids[DB_ID_KEYS[node_type]]


class TestDeviceConfig(BaseTest):

    @pytest.mark.smoke
    @pytest.mark.parametrize("node_type, node_label", _BL, ids=_BL_IDS)
    @pytest.mark.parametrize("enabled", [1, 0], ids=["enable", "disable"])
    def test_backlight(self, node_type, node_label, enabled, node_ids):
        response = self.configuration_page().set_backlight(
            node_ids[node_type], node_label, _db_id(node_ids, node_type), enabled
        )
        assert response["bl"] == enabled and response["rc"] == 0

    @pytest.mark.regression
    @pytest.mark.parametrize("node_type, node_label, threshold", _TH, ids=_TH_IDS)
    def test_touch_threshold(self, node_type, node_label, threshold, node_ids):
        response = self.configuration_page().set_threshold(
            node_ids[node_type], node_label, _db_id(node_ids, node_type), threshold
        )
        assert response["th"] == threshold and response["rc"] == 0

    @pytest.mark.regression
    @pytest.mark.parametrize("level", TestData.onstate_levels())
    def test_fan_dimmer_onstate_level(self, level, node_ids):
        response = self.configuration_page().set_onstate_level(
            node_ids["fd"], "FD", node_ids["FdDbId"], level
        )
        assert response["ol"] == level and response["rc"] == 0
