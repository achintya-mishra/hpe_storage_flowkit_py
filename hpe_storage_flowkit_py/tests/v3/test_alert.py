#    (c) Copyright 2026 Hewlett Packard Enterprise Development LP
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
import unittest
from unittest.mock import MagicMock, Mock, patch
import sys
import os
import time

# Ensure src is on sys.path for direct imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hpe_storage_flowkit_py.v3.workflows.alert import AlertWorkflow
from hpe_storage_flowkit_py.v3.core import exceptions
from hpe_storage_flowkit_py.v3.core.rest_client import RESTClient
from hpe_storage_flowkit_py.v3.validators.alert_validator import (
    validate_filter_params, validate_test_alert_params
)


class MockTaskManager:
    """Mock TaskManager for testing alert workflows."""
    def __init__(self, session_mgr):
        self.session_mgr = session_mgr

    def wait_for_task_to_end(self, task_uri):
        return {"status": "STATE_FINISHED", "state": {"overall": "STATE_NORMAL"}}


class TestAlertWorkflow(unittest.TestCase):
    """Unit tests for AlertWorkflow class using a simple Mock REST client."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.session_client = Mock()
        self.session_client.rest_client = Mock(spec=RESTClient)
        # Default canned responses
        self.session_client.rest_client.get.return_value = {"members": {}}
        self.session_client.rest_client.post.return_value = {"status": "success"}
        self.task_mgr = MockTaskManager(self.session_client)
        self.workflow = AlertWorkflow(self.session_client, self.task_mgr)

    def _simulate_alerts_list(self, alerts=None):
        """Helper to simulate multiple alerts response."""
        if alerts is None:
            alerts = [
                {"uid": "alert-uid-1", "status": "STATUS_NEW", "type": "TYPE_CUSTOMER", "id": 1,
                 "originEvent": {"severity": "SEVERITY_CRITICAL"},
                 "lastTime": {"ms": int(time.time() * 1000)}},
                {"uid": "alert-uid-2", "status": "STATUS_ACKNOWLEDGED", "type": "TYPE_SERVICE", "id": 2,
                 "originEvent": {"severity": "SEVERITY_MINOR"},
                 "lastTime": {"ms": int(time.time() * 1000)}}
            ]
        members = {}
        for i, alert in enumerate(alerts):
            members[f"member-{i}"] = alert
        self.session_client.rest_client.get.return_value = {"members": members}

    def _simulate_alerts_with_old_time(self):
        """Helper to simulate alerts with varying timestamps."""
        now_ms = int(time.time() * 1000)
        day_ms = 86400 * 1000
        alerts = [
            {"uid": "recent-1", "status": "STATUS_NEW", "type": "TYPE_CUSTOMER",
             "originEvent": {"severity": "SEVERITY_CRITICAL"},
             "lastTime": {"ms": now_ms - (1 * day_ms)}},  # 1 day ago
            {"uid": "recent-2", "status": "STATUS_NEW", "type": "TYPE_SERVICE",
             "originEvent": {"severity": "SEVERITY_MAJOR"},
             "lastTime": {"ms": now_ms - (2 * day_ms)}},  # 2 days ago
            {"uid": "old-1", "status": "STATUS_FIXED", "type": "TYPE_CUSTOMER",
             "originEvent": {"severity": "SEVERITY_MINOR"},
             "lastTime": {"ms": now_ms - (10 * day_ms)}},  # 10 days ago
        ]
        members = {}
        for i, alert in enumerate(alerts):
            members[f"member-{i}"] = alert
        self.session_client.rest_client.get.return_value = {"members": members}

    # ---- get_alerts tests (no filters = get all) ----

    def test_get_alerts_no_filters_success(self):
        """Test successful retrieval of all alerts with no filters."""
        self._simulate_alerts_list()
        result = self.workflow.get_alerts()
        self.session_client.rest_client.get.assert_called_once_with("/alerts")
        self.assertEqual(len(result), 2)

    def test_get_alerts_no_filters_empty(self):
        """Test retrieval of alerts when none exist."""
        self.session_client.rest_client.get.return_value = {"members": {}}
        result = self.workflow.get_alerts()
        self.session_client.rest_client.get.assert_called_once_with("/alerts")
        self.assertEqual(len(result), 0)

    def test_get_alerts_unauthorized(self):
        """Test get alerts with authentication error."""
        error = Exception("401 Unauthorized")
        error.status_code = 401
        self.session_client.rest_client.get.side_effect = error
        with self.assertRaises(Exception):
            self.workflow.get_alerts()

    def test_get_alerts_forbidden(self):
        """Test get alerts with insufficient privileges."""
        error = Exception("403 Forbidden")
        error.status_code = 403
        self.session_client.rest_client.get.side_effect = error
        with self.assertRaises(Exception):
            self.workflow.get_alerts()

    def test_get_alerts_generic_error(self):
        """Test get alerts with generic error."""
        self.session_client.rest_client.get.side_effect = Exception("500 Internal Server Error")
        with self.assertRaises(Exception):
            self.workflow.get_alerts()

    # ---- get_alerts tests (with filters) ----

    def test_get_alerts_filtered_by_type(self):
        """Test filtering alerts by type."""
        self._simulate_alerts_list()
        result = self.workflow.get_alerts(alert_type="TYPE_CUSTOMER")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "TYPE_CUSTOMER")

    def test_get_alerts_filtered_by_type_no_match(self):
        """Test filtering alerts by type with no matches."""
        self._simulate_alerts_list()
        result = self.workflow.get_alerts(alert_type="TYPE_APPLICATION")
        self.assertEqual(len(result), 0)

    def test_get_alerts_filtered_by_status(self):
        """Test filtering alerts by status."""
        self._simulate_alerts_list()
        result = self.workflow.get_alerts(status="STATUS_NEW")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "STATUS_NEW")

    def test_get_alerts_filtered_by_severity(self):
        """Test filtering alerts by severity."""
        self._simulate_alerts_list()
        result = self.workflow.get_alerts(severity="SEVERITY_CRITICAL")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["originEvent"]["severity"], "SEVERITY_CRITICAL")

    def test_get_alerts_filtered_by_last_days(self):
        """Test filtering alerts by last N days."""
        self._simulate_alerts_with_old_time()
        result = self.workflow.get_alerts(last_days=3)
        # Should get 2 recent alerts, not the 10-day-old one
        self.assertEqual(len(result), 2)
        uids = [a["uid"] for a in result]
        self.assertIn("recent-1", uids)
        self.assertIn("recent-2", uids)
        self.assertNotIn("old-1", uids)

    def test_get_alerts_filtered_by_last_hours(self):
        """Test filtering alerts by last N hours."""
        self._simulate_alerts_with_old_time()
        result = self.workflow.get_alerts(last_hours=12)
        # All alerts are at least 1 day old, so none should match 12 hours
        self.assertEqual(len(result), 0)

    def test_get_alerts_filtered_combined_filters(self):
        """Test filtering with multiple combined filters."""
        self._simulate_alerts_with_old_time()
        result = self.workflow.get_alerts(
            alert_type="TYPE_CUSTOMER",
            last_days=5
        )
        # Only recent-1 is TYPE_CUSTOMER and within 5 days
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uid"], "recent-1")

    def test_get_alerts_filtered_type_and_severity(self):
        """Test filtering with type and severity."""
        self._simulate_alerts_list()
        result = self.workflow.get_alerts(
            alert_type="TYPE_CUSTOMER",
            severity="SEVERITY_CRITICAL"
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uid"], "alert-uid-1")

    def test_get_alerts_filtered_type_severity_no_match(self):
        """Test filtering with type + severity combination that has no match."""
        self._simulate_alerts_list()
        result = self.workflow.get_alerts(
            alert_type="TYPE_SERVICE",
            severity="SEVERITY_CRITICAL"
        )
        self.assertEqual(len(result), 0)

    def test_get_alerts_filtered_invalid_type(self):
        """Test filtering with invalid alert type."""
        with self.assertRaises(exceptions.InvalidInput) as context:
            self.workflow.get_alerts(alert_type="INVALID_TYPE")
        self.assertIn("Invalid alert type", str(context.exception))

    def test_get_alerts_filtered_invalid_severity(self):
        """Test filtering with invalid severity."""
        with self.assertRaises(exceptions.InvalidInput) as context:
            self.workflow.get_alerts(severity="INVALID_SEVERITY")
        self.assertIn("Invalid severity", str(context.exception))

    def test_get_alerts_filtered_invalid_status(self):
        """Test filtering with invalid status."""
        with self.assertRaises(exceptions.InvalidInput) as context:
            self.workflow.get_alerts(status="INVALID_STATUS")
        self.assertIn("Invalid alert status", str(context.exception))

    def test_get_alerts_filtered_both_days_and_hours(self):
        """Test filtering with both last_days and last_hours raises error."""
        with self.assertRaises(exceptions.InvalidInput) as context:
            self.workflow.get_alerts(last_days=3, last_hours=12)
        self.assertIn("Cannot specify both", str(context.exception))

    def test_get_alerts_filtered_negative_days(self):
        """Test filtering with negative last_days."""
        with self.assertRaises(exceptions.InvalidInput) as context:
            self.workflow.get_alerts(last_days=-1)
        self.assertIn("positive number", str(context.exception))

    def test_get_alerts_filtered_negative_hours(self):
        """Test filtering with negative last_hours."""
        with self.assertRaises(exceptions.InvalidInput) as context:
            self.workflow.get_alerts(last_hours=-1)
        self.assertIn("positive number", str(context.exception))

    def test_get_alerts_filtered_zero_days(self):
        """Test filtering with zero last_days."""
        with self.assertRaises(exceptions.InvalidInput):
            self.workflow.get_alerts(last_days=0)

    def test_get_alerts_filtered_unauthorized(self):
        """Test filtered get with authentication error."""
        error = Exception("401 Unauthorized")
        error.status_code = 401
        self.session_client.rest_client.get.side_effect = error
        with self.assertRaises(Exception):
            self.workflow.get_alerts(alert_type="TYPE_CUSTOMER")

    def test_get_alerts_filtered_api_error(self):
        """Test filtered get with generic API error."""
        self.session_client.rest_client.get.side_effect = Exception("500 Server Error")
        with self.assertRaises(Exception):
            self.workflow.get_alerts()

    def test_get_alerts_filtered_empty_response(self):
        """Test filtered get with empty response."""
        self.session_client.rest_client.get.return_value = {"members": {}}
        result = self.workflow.get_alerts(alert_type="TYPE_CUSTOMER")
        self.assertEqual(len(result), 0)

    # ---- test_alert tests ----

    def test_test_alert_success_with_message(self):
        """Test successful test alert generation with message."""
        self.workflow.test_alert("This is a test alert")
        self.session_client.rest_client.post.assert_called_once()
        call_args = self.session_client.rest_client.post.call_args
        self.assertEqual(call_args[0][0], "/alerts/custom")
        payload = call_args[0][1]
        self.assertEqual(payload["action"], "TEST_ALERT")
        self.assertEqual(payload["parameters"]["message"], "This is a test alert")

    def test_test_alert_success_without_message(self):
        """Test successful test alert generation without message."""
        self.workflow.test_alert()
        call_args = self.session_client.rest_client.post.call_args
        payload = call_args[0][1]
        self.assertEqual(payload["action"], "TEST_ALERT")
        self.assertEqual(payload["parameters"], {})

    def test_test_alert_empty_message(self):
        """Test test alert with empty message."""
        with self.assertRaises(exceptions.InvalidInput) as context:
            self.workflow.test_alert("  ")
        self.assertIn("cannot be empty", str(context.exception))

    def test_test_alert_api_error(self):
        """Test test alert with API error."""
        self.session_client.rest_client.post.side_effect = Exception("500 Internal Server Error")
        with self.assertRaises(Exception):
            self.workflow.test_alert("test message")

    # ---- _parse_alerts_response tests ----

    def test_parse_alerts_response_dict_with_members(self):
        """Test parsing dict response with members."""
        response = {"members": {"m1": {"uid": "a1"}, "m2": {"uid": "a2"}}}
        result = self.workflow._parse_alerts_response(response)
        self.assertEqual(len(result), 2)

    def test_parse_alerts_response_list(self):
        """Test parsing list response."""
        response = [{"uid": "a1"}, {"uid": "a2"}]
        result = self.workflow._parse_alerts_response(response)
        self.assertEqual(len(result), 2)

    def test_parse_alerts_response_empty_members(self):
        """Test parsing dict response with empty members."""
        response = {"members": {}}
        result = self.workflow._parse_alerts_response(response)
        self.assertEqual(len(result), 0)

    def test_parse_alerts_response_none(self):
        """Test parsing None response."""
        result = self.workflow._parse_alerts_response(None)
        self.assertEqual(len(result), 0)

    # ---- _build payload tests ----

    def test_build_test_alert_payload_with_message(self):
        """Test building test alert payload with message."""
        payload = self.workflow._build_test_alert_payload("Hello test")
        expected = {
            "action": "TEST_ALERT",
            "parameters": {"message": "Hello test"}
        }
        self.assertEqual(payload, expected)

    def test_build_test_alert_payload_without_message(self):
        """Test building test alert payload without message."""
        payload = self.workflow._build_test_alert_payload()
        expected = {
            "action": "TEST_ALERT",
            "parameters": {}
        }
        self.assertEqual(payload, expected)

    # ---- _filter_alerts tests ----

    def test_filter_alerts_by_type(self):
        """Test _filter_alerts with type filter."""
        alerts = [
            {"type": "TYPE_CUSTOMER", "status": "STATUS_NEW"},
            {"type": "TYPE_SERVICE", "status": "STATUS_NEW"}
        ]
        result = self.workflow._filter_alerts(alerts, alert_type="TYPE_CUSTOMER")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "TYPE_CUSTOMER")

    def test_filter_alerts_by_status(self):
        """Test _filter_alerts with status filter."""
        alerts = [
            {"type": "TYPE_CUSTOMER", "status": "STATUS_NEW"},
            {"type": "TYPE_SERVICE", "status": "STATUS_FIXED"}
        ]
        result = self.workflow._filter_alerts(alerts, status="STATUS_FIXED")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "STATUS_FIXED")

    def test_filter_alerts_by_severity(self):
        """Test _filter_alerts with severity filter."""
        alerts = [
            {"originEvent": {"severity": "SEVERITY_CRITICAL"}},
            {"originEvent": {"severity": "SEVERITY_MINOR"}}
        ]
        result = self.workflow._filter_alerts(alerts, severity="SEVERITY_CRITICAL")
        self.assertEqual(len(result), 1)

    def test_filter_alerts_missing_origin_event(self):
        """Test _filter_alerts with alerts missing originEvent."""
        alerts = [
            {"status": "STATUS_NEW"},  # no originEvent
            {"status": "STATUS_NEW", "originEvent": {"severity": "SEVERITY_CRITICAL"}}
        ]
        result = self.workflow._filter_alerts(alerts, severity="SEVERITY_CRITICAL")
        self.assertEqual(len(result), 1)

    def test_filter_alerts_by_time_days(self):
        """Test _filter_alerts with last_days."""
        now_ms = int(time.time() * 1000)
        day_ms = 86400 * 1000
        alerts = [
            {"uid": "new", "lastTime": {"ms": now_ms - (1 * day_ms)}},
            {"uid": "old", "lastTime": {"ms": now_ms - (10 * day_ms)}}
        ]
        result = self.workflow._filter_alerts(alerts, last_days=3)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uid"], "new")

    def test_filter_alerts_by_time_hours(self):
        """Test _filter_alerts with last_hours."""
        now_ms = int(time.time() * 1000)
        hour_ms = 3600 * 1000
        alerts = [
            {"uid": "recent", "lastTime": {"ms": now_ms - (2 * hour_ms)}},
            {"uid": "older", "lastTime": {"ms": now_ms - (48 * hour_ms)}}
        ]
        result = self.workflow._filter_alerts(alerts, last_hours=6)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uid"], "recent")

    def test_filter_alerts_no_last_time(self):
        """Test _filter_alerts with time filter on alerts missing lastTime."""
        alerts = [
            {"uid": "no-time"},  # no lastTime
            {"uid": "has-time", "lastTime": {"ms": int(time.time() * 1000)}}
        ]
        result = self.workflow._filter_alerts(alerts, last_days=1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uid"], "has-time")


class TestAlertValidator(unittest.TestCase):
    """Unit tests for alert validator functions."""

    # ---- validate_filter_params tests ----

    def test_validate_filter_params_all_none(self):
        """Test validation with all None parameters."""
        validate_filter_params()  # Should not raise

    def test_validate_filter_params_valid_type(self):
        """Test validation with valid type."""
        validate_filter_params(alert_type="TYPE_CUSTOMER")

    def test_validate_filter_params_valid_severity(self):
        """Test validation with valid severity."""
        validate_filter_params(severity="SEVERITY_CRITICAL")

    def test_validate_filter_params_valid_status(self):
        """Test validation with valid status."""
        validate_filter_params(status="STATUS_NEW")

    def test_validate_filter_params_valid_last_days(self):
        """Test validation with valid last_days."""
        validate_filter_params(last_days=3)

    def test_validate_filter_params_valid_last_hours(self):
        """Test validation with valid last_hours."""
        validate_filter_params(last_hours=12)

    def test_validate_filter_params_valid_combined(self):
        """Test validation with multiple valid params."""
        validate_filter_params(
            alert_type="TYPE_SERVICE",
            severity="SEVERITY_MAJOR",
            status="STATUS_ACKNOWLEDGED",
            last_days=7
        )

    def test_validate_filter_params_invalid_type(self):
        """Test validation with invalid type."""
        with self.assertRaises(exceptions.InvalidInput):
            validate_filter_params(alert_type="INVALID")

    def test_validate_filter_params_invalid_severity(self):
        """Test validation with invalid severity."""
        with self.assertRaises(exceptions.InvalidInput):
            validate_filter_params(severity="INVALID")

    def test_validate_filter_params_invalid_status(self):
        """Test validation with invalid status."""
        with self.assertRaises(exceptions.InvalidInput):
            validate_filter_params(status="INVALID")

    def test_validate_filter_params_both_time(self):
        """Test validation with both last_days and last_hours."""
        with self.assertRaises(exceptions.InvalidInput):
            validate_filter_params(last_days=3, last_hours=12)

    def test_validate_filter_params_negative_days(self):
        """Test validation with negative last_days."""
        with self.assertRaises(exceptions.InvalidInput):
            validate_filter_params(last_days=-1)

    def test_validate_filter_params_zero_days(self):
        """Test validation with zero last_days."""
        with self.assertRaises(exceptions.InvalidInput):
            validate_filter_params(last_days=0)

    def test_validate_filter_params_negative_hours(self):
        """Test validation with negative last_hours."""
        with self.assertRaises(exceptions.InvalidInput):
            validate_filter_params(last_hours=-5)

    def test_validate_filter_params_type_not_string(self):
        """Test validation with non-string type."""
        with self.assertRaises(exceptions.InvalidInput):
            validate_filter_params(alert_type=123)

    def test_validate_filter_params_days_not_number(self):
        """Test validation with non-number last_days."""
        with self.assertRaises(exceptions.InvalidInput):
            validate_filter_params(last_days="three")

    # ---- validate_test_alert_params tests ----

    def test_validate_test_alert_params_valid_message(self):
        """Test valid test alert message."""
        validate_test_alert_params("Hello test")

    def test_validate_test_alert_params_none_message(self):
        """Test None message (optional)."""
        validate_test_alert_params(None)  # Should not raise

    def test_validate_test_alert_params_empty_message(self):
        """Test empty message."""
        with self.assertRaises(exceptions.InvalidInput):
            validate_test_alert_params("  ")

    def test_validate_test_alert_params_non_string_message(self):
        """Test non-string message."""
        with self.assertRaises(exceptions.InvalidInput):
            validate_test_alert_params(123)


if __name__ == '__main__':
    unittest.main()
