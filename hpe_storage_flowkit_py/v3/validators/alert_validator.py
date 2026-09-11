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
"""Alert Validator.

This module provides validation functions for alert management parameters.
"""

from hpe_storage_flowkit_py.v3.core import exceptions
from hpe_storage_flowkit_py.v3.utils.constants import (
    ALERT_SEVERITIES,
    ALERT_STATUSES,
    ALERT_TYPES,
)

# All valid alert statuses
VALID_ALERT_STATUSES = list(ALERT_STATUSES)

# Valid alert types
VALID_ALERT_TYPES = list(ALERT_TYPES)

# Valid event severities
VALID_ALERT_SEVERITIES = list(ALERT_SEVERITIES)


def validate_filter_params(alert_type=None, severity=None, status=None,
                           last_days=None, last_hours=None):
    """Validate filter parameters for alert queries.

    Args:
        alert_type (str, optional): Alert type filter
        severity (str, optional): Event severity filter
        status (str, optional): Alert status filter
        last_days (int/float, optional): Show alerts from last N days
        last_hours (int/float, optional): Show alerts from last N hours

    Raises:
        exceptions.InvalidInput: If validation fails
    """
    if alert_type is not None:
        if not isinstance(alert_type, str):
            raise exceptions.InvalidInput("Alert type must be a string")
        if alert_type not in VALID_ALERT_TYPES:
            raise exceptions.InvalidInput(
                f"Invalid alert type '{alert_type}'. "
                f"Must be one of: {', '.join(VALID_ALERT_TYPES)}"
            )

    if severity is not None:
        if not isinstance(severity, str):
            raise exceptions.InvalidInput("Severity must be a string")
        if severity not in VALID_ALERT_SEVERITIES:
            raise exceptions.InvalidInput(
                f"Invalid severity '{severity}'. "
                f"Must be one of: {', '.join(VALID_ALERT_SEVERITIES)}"
            )

    if status is not None:
        if not isinstance(status, str):
            raise exceptions.InvalidInput("Alert status must be a string")
        if status not in VALID_ALERT_STATUSES:
            raise exceptions.InvalidInput(
                f"Invalid alert status '{status}'. "
                f"Must be one of: {', '.join(VALID_ALERT_STATUSES)}"
            )

    if last_days is not None and last_hours is not None:
        raise exceptions.InvalidInput(
            "Cannot specify both 'last_days' and 'last_hours'. Use one at a time."
        )

    if last_days is not None:
        if not isinstance(last_days, (int, float)):
            raise exceptions.InvalidInput("last_days must be a number")
        if last_days <= 0:
            raise exceptions.InvalidInput("last_days must be a positive number")

    if last_hours is not None:
        if not isinstance(last_hours, (int, float)):
            raise exceptions.InvalidInput("last_hours must be a number")
        if last_hours <= 0:
            raise exceptions.InvalidInput("last_hours must be a positive number")


def validate_test_alert_params(message=None):
    """Validate parameters for test alert generation.

    Args:
        message (str, optional): Test message to validate

    Raises:
        exceptions.InvalidInput: If validation fails
    """
    if message is not None:
        if not isinstance(message, str):
            raise exceptions.InvalidInput("Test alert message must be a string")

        if not message.strip():
            raise exceptions.InvalidInput("Test alert message cannot be empty")
