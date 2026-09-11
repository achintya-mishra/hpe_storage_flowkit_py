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
"""Alert workflow implementation for HPE Alletra MP storage systems.

This module provides alert management operations:
  - Get alerts with optional filters (GET /api/v3/alerts + client-side filtering)
  - Generate test alert (POST /api/v3/alerts/custom with TEST_ALERT action)

Supported filters for get_alerts:
  - type: TYPE_UNKNOWN, TYPE_CUSTOMER, TYPE_SERVICE, TYPE_APPLICATION
  - status: STATUS_UNKNOWN, STATUS_NEW, STATUS_ACKNOWLEDGED, STATUS_FIXED,
            STATUS_REMOVED, STATUS_AUTOFIXED
  - severity: SEVERITY_UNKNOWN, SEVERITY_FATAL, SEVERITY_CRITICAL, SEVERITY_MAJOR,
              SEVERITY_MINOR, SEVERITY_DEGRADED, SEVERITY_INFO, SEVERITY_DEBUG
  - time: last_days or last_hours (alerts within a recent time window)

Endpoint: /api/v3/alerts

Return convention:
  On success: raw RESTClient parsed response
  On failure (caught exception): raises appropriate exception
"""

import logging
import time as _time

from hpe_storage_flowkit_py.v3.core import exceptions
from hpe_storage_flowkit_py.v3.core.session import SessionManager
from hpe_storage_flowkit_py.v3.workflows.task import TaskManager
from hpe_storage_flowkit_py.v3.validators.alert_validator import (
    validate_filter_params, validate_test_alert_params
)
from hpe_storage_flowkit_py.v3.utils.utils import handle_async_response

logger = logging.getLogger('flowkit')


class AlertWorkflow:
    """Workflow encapsulating alert management operations.

    Success path returns underlying REST response (or None when API returns no body).
    Non-changed idempotent situations raise specific exceptions that the Ansible
    module maps to an unchanged result.
    """

    def __init__(self, session_mgr: SessionManager, task_manager: TaskManager):
        self.session_mgr = session_mgr
        self.task_manager = task_manager

    def _parse_alerts_response(self, alerts_response):
        """Parse alerts API response into list of alert dicts."""
        if isinstance(alerts_response, dict):
            if 'members' in alerts_response and alerts_response['members']:
                return list(alerts_response['members'].values())
        elif isinstance(alerts_response, list):
            return alerts_response
        elif alerts_response is not None:
            logger.warning(
                f"Unexpected alerts response type: {type(alerts_response).__name__}"
            )
        return []

    def _build_test_alert_payload(self, message=None):
        """Build payload for test alert generation (POST /api/v3/alerts/custom).

        Args:
            message (str, optional): Test message to include in the alert

        Returns:
            dict: API payload
        """
        logger.debug("Building test alert payload")
        payload = {
            "action": "TEST_ALERT",
            "parameters": {}
        }
        if message:
            payload["parameters"]["message"] = message
        logger.debug(f"Built test alert payload: {payload}")
        return payload

    def _filter_alerts(self, alerts, alert_type=None, severity=None,
                       status=None, last_days=None, last_hours=None):
        """Apply client-side filters to a list of alert dicts.

        Args:
            alerts (list): List of alert dicts from _parse_alerts_response
            alert_type (str, optional): Filter by alert type (top-level 'type' field)
            severity (str, optional): Filter by origin event severity
            status (str, optional): Filter by alert status (top-level 'status' field)
            last_days (int/float, optional): Only return alerts from the last N days
            last_hours (int/float, optional): Only return alerts from the last N hours

        Returns:
            list: Filtered list of alert dicts
        """
        filtered = alerts

        if alert_type is not None:
            logger.debug(f"Filtering alerts by type: {alert_type}")
            filtered = [a for a in filtered if a.get('type') == alert_type]

        if status is not None:
            logger.debug(f"Filtering alerts by status: {status}")
            filtered = [a for a in filtered if a.get('status') == status]

        if severity is not None:
            logger.debug(f"Filtering alerts by severity: {severity}")
            filtered = [
                a for a in filtered
                if a.get('originEvent', {}).get('severity') == severity
            ]

        if last_days is not None or last_hours is not None:
            if last_days is not None:
                cutoff_ms = int((_time.time() - last_days * 86400) * 1000)
                label = f"{last_days} day(s)"
            else:
                cutoff_ms = int((_time.time() - last_hours * 3600) * 1000)
                label = f"{last_hours} hour(s)"

            logger.debug(f"Filtering alerts from last {label} (cutoff epoch ms: {cutoff_ms})")
            filtered = [
                a for a in filtered
                if a.get('lastTime', {}).get('ms', 0) >= cutoff_ms
            ]

        logger.debug(f"Filter result: {len(filtered)} alert(s) matched out of {len(alerts)}")
        return filtered

    # ---- Operations ----

    def _execute_get_alerts(self, alert_type=None, severity=None,
                            status=None, last_days=None, last_hours=None):
        """Execute alert retrieval with optional filtering.

        Fetches all alerts from the API. If any filter is provided, applies
        client-side filtering and returns a parsed list. If no filters are
        provided, returns all alerts as a parsed list.
        """
        logger.info("Getting alerts")
        logger.debug(
            f"Filter params: type={alert_type}, severity={severity}, "
            f"status={status}, last_days={last_days}, last_hours={last_hours}"
        )

        has_filters = any(p is not None for p in [alert_type, severity, status, last_days, last_hours])

        if has_filters:
            validate_filter_params(alert_type, severity, status, last_days, last_hours)

        endpoint = "/alerts"
        logger.info(f"Making GET request to {endpoint}")
        response = self.session_mgr.rest_client.get(endpoint)
        logger.info("Successfully retrieved all alerts")

        all_alerts = self._parse_alerts_response(response)

        if has_filters:
            filtered = self._filter_alerts(
                all_alerts,
                alert_type=alert_type,
                severity=severity,
                status=status,
                last_days=last_days,
                last_hours=last_hours
            )
            logger.info(f"Filtered {len(all_alerts)} alerts down to {len(filtered)}")
            return filtered

        logger.info(f"Returning all {len(all_alerts)} alerts")
        return all_alerts

    def get_alerts(self, alert_type=None, severity=None,
                   status=None, last_days=None, last_hours=None):
        """Get alerts with optional filters (GET /api/v3/alerts + client-side filtering).

        If no filters are provided, returns all alerts.
        If any filter is provided, returns only matching alerts.

        Args:
            alert_type (str, optional): Filter by type
            severity (str, optional): Filter by origin event severity
            status (str, optional): Filter by alert status
            last_days (int/float, optional): Show alerts from last N days
            last_hours (int/float, optional): Show alerts from last N hours

        Returns:
            list: Alert dicts (all or filtered)
        """
        logger.info(
            f">>>>>>>Entered get_alerts: type={alert_type}, severity={severity}, "
            f"status={status}, last_days={last_days}, last_hours={last_hours}"
        )
        try:
            return self._execute_get_alerts(
                alert_type=alert_type,
                severity=severity,
                status=status,
                last_days=last_days,
                last_hours=last_hours
            )
        except Exception as e:
            logger.exception(f"Failed to get alerts due to error: {e}")
            raise
        finally:
            logger.info(f"<<<<<<<Exited get_alerts")

    def _execute_test_alert(self, message=None):
        """Execute test alert generation operation."""
        logger.info(f"Starting test alert generation")
        logger.debug(f"Validating test alert parameters")

        validate_test_alert_params(message)

        payload = self._build_test_alert_payload(message)

        logger.info(f"Generating test alert")
        endpoint = "/alerts/custom"
        logger.debug(f"Making POST request to {endpoint}")

        try:
            response = self.session_mgr.rest_client.post(endpoint, payload)
            result = handle_async_response(self.task_manager, "test alert", "custom", response)
            logger.info(f"Test alert generated successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to generate test alert: {str(e)}")
            raise

    def test_alert(self, message=None):
        """Generate a test alert (POST /api/v3/alerts/custom with TEST_ALERT action)."""
        logger.info(f">>>>>>>Entered test_alert: message='{message}'")
        try:
            return self._execute_test_alert(message)
        except Exception as e:
            logger.exception(f"Failed to generate test alert due to error: {e}")
            raise
        finally:
            logger.info(f"<<<<<<<Exited test_alert")
