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
"""
Configuration defaults for HPE Storage FlowKit
Users can override these values by modifying this file
"""

# Task polling configuration
TASK_POLL_RATE_SECS = 3  # Default polling interval in seconds
TASK_TIMEOUT_SECS = 1200  # Default timeout in seconds (20 minutes)

# Remote Copy Group actions
RC_GROUP_ADMIT_HOST = 'RC_GROUP_ADMIT_HOST'

# Alert workflow enums
ALERT_STATUSES = (
    'STATUS_UNKNOWN', 'STATUS_NEW', 'STATUS_ACKNOWLEDGED',
    'STATUS_FIXED', 'STATUS_REMOVED', 'STATUS_AUTOFIXED'
)

ALERT_TYPES = (
    'TYPE_UNKNOWN', 'TYPE_CUSTOMER', 'TYPE_SERVICE', 'TYPE_APPLICATION'
)

ALERT_SEVERITIES = (
    'SEVERITY_UNKNOWN', 'SEVERITY_FATAL', 'SEVERITY_CRITICAL',
    'SEVERITY_MAJOR', 'SEVERITY_MINOR', 'SEVERITY_DEGRADED',
    'SEVERITY_INFO', 'SEVERITY_DEBUG'
)