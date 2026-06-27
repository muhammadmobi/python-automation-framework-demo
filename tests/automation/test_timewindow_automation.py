"""Time-window automation — ordered Create -> Edit -> Delete."""
import pytest

from tests.base.base_test import BaseTest
from tests.data.test_data import TestData

AID = SID = 65272


class TestTimeWindowAutomation(BaseTest):

    @pytest.mark.smoke
    @pytest.mark.dependency(name="create_automation")
    def test_create_automation(self, node_ids):
        response = self.automation_page().create(AID, SID, TestData.all_node_devices(node_ids))
        assert response["aid"] == AID and response["sid"] == SID and response["rc"] == 0
        assert all(device["rc"] == 0 for device in response["devices"])

    @pytest.mark.regression
    @pytest.mark.dependency(name="edit_automation", depends=["create_automation"])
    def test_edit_automation(self, node_ids):
        response = self.automation_page().edit(
            AID,
            SID,
            add={"SP": [{"id": node_ids["sp"], "s": 0}]},
            edit={"TP": [{"id": node_ids["1g"], "s": 0}]},
        )
        assert response["aid"] == AID and response["rc"] == 0

    @pytest.mark.regression
    @pytest.mark.dependency(name="delete_automation", depends=["edit_automation"])
    def test_delete_automation(self):
        assert self.automation_page().delete(AID, SID)["rc"] == 0
