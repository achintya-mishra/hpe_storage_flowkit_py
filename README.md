<!--
(c) Copyright 2026 Hewlett Packard Enterprise Development LP  
All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
-->
# HPE Storage FlowKit (Python)

A Python client library for interacting with HPE Alletra MP storage arrays.

## Overview

HPE Storage FlowKit is a comprehensive Python client designed to interact with the HPE Alletra MP storage platform. It provides a simple and intuitive API for automating configuration, management, and monitoring tasks via the array's REST web service interface (WSAPI).

The library provides control over  **high-level service clients** (Cinder) for common integration scenarios.

## Requirements

To use this library, your environment must meet the following requirements:

- **HPE Alletra MP OS**: Version **10.5** or later
- **Python**: Version **3.10** or later
- **Network Access**: HTTPS connectivity to the storage array's management interface
- **WSAPI Service**: Must be enabled on the storage array

Ensure the WSAPI service is enabled on the storage array before using the client.

## Installation

```bash
pip install hpe-storage-flowkit-py
```

## Capabilities

### Volume Operations
- Create Volume
- Delete Volume
- Modify Volume
- Grow Volume
- Tune Volume
- Extend Volume
- Create Cloned Volume
- Migrate Volume
- Retype Volume

### Volume Set Operations
- Create Volume Set
- Delete Volume Set
- Modify Volume Set
- Add Volumes to Volume Set
- Remove Volumes from Volume Set

### Snapshot Operations
- Create Snapshot
- Modify Snapshot
- Delete Snapshot
- Restore Offline Snapshot
- Restore Online Snapshot
- Revert to Snapshot
- Create Volume from Snapshot
- Create Snapshot Schedule
- Modify Snapshot Schedule
- Suspend Snapshot Schedule
- Resume Snapshot Schedule
- Delete Snapshot Schedule

### Online Clone Operations
- Create Online Clone
- Delete Online Clone

### Offline Clone Operations
- Create Offline Clone
- Delete Offline Clone
- Resync Offline Clone
- Stop Offline Clone

### CPG Operations
- Create CPG
- Delete CPG
- Get CPG

### Host Operations
- Create Host
- Delete Host
- Modify Host
- Add FC Path to Host
- Remove FC Path from Host
- Add iSCSI Path to Host
- Remove iSCSI Path from Host
- Add Initiator CHAP
- Remove Initiator CHAP
- Add Target CHAP
- Remove Target CHAP

### Host Set Operations
- Create Host Set
- Delete Host Set
- Add Hosts to Host Set
- Remove Hosts from Host Set

### VLUN Operations
- Export Volume to Host
- Export Volume to Host Set
- Export Volume Set to Host
- Export Volume Set to Host Set
- Unexport Volume from Host
- Unexport Volume from Host Set
- Unexport Volume Set from Host
- Unexport Volume Set from Host Set
- Terminate Connection

### QoS Operations
- Create QoS Rule
- Modify QoS Rule
- Delete QoS Rule
- Get QoS Rule
- List QoS Rules

### Remote Copy Operations
- Create Remote Copy Group
- Delete Remote Copy Group
- Modify Remote Copy Group
- Add Volume to Remote Copy Group
- Remove Volume from Remote Copy Group
- Start Remote Copy Group
- Stop Remote Copy Group
- Synchronize Remote Copy Group
- Admit Remote Copy Link
- Dismiss Remote Copy Link
- Admit Remote Copy Target
- Dismiss Remote Copy Target
- Start Remote Copy Service
- Get Remote Copy Status
- Failover Replication
- Failover Host

### Group Operations
- Create Group
- Delete Group
- Update Group
- Create Group from Source
- Create Group Snapshot
- Delete Group Snapshot

### System Configuration
- Configure DNS Network
- Configure Date/Time (NTP)

### User Management
- Create User
- Modify User
- Delete User
- Get User
- Get All Users

### Certificate Management
- Create Certificate
- Patch Certificate
- Patch Certificate by Name
- Delete Certificate
- Delete Certificate by Name
- Get Certificate
- Get Certificate by Name
- Get All Certificates

### Alert Management
- Get Alerts
- Generate Test Alert

### Storage Management
- Manage Existing Volume
- Unmanage Volume
- Get Manageable Volumes
- Manage Existing Snapshot
- Unmanage Snapshot
- Get Manageable Snapshots
- Get Volume Statistics

## Testing

### Prerequisites

Install the required testing dependencies:

```bash
pip install pytest mock
```

### Running Unit Tests

Run all tests:

```bash
python3 -m pytest v1/test v3/test --import-mode=importlib
```

Run a specific test file:

```bash
python3 -m pytest v3/test/<test_file_name.py> --import-mode=importlib
```

For example:

```bash
python3 -m pytest v3/test/test_volume.py --import-mode=importlib
```

Run a specific test method:

```bash
python3 -m pytest v3/test/<test_file_name.py>::TestClassName::test_method_name --import-mode=importlib
```
Note: Make sure to run the commands from inside the `hpe_storage_flowkit_py` directory.

## License

This project is released under the **Apache License 2.0**.

See [LICENSE.txt](LICENSE.txt) for full license details.

---

**Copyright** (c) 2026 Hewlett Packard Enterprise Development LP
