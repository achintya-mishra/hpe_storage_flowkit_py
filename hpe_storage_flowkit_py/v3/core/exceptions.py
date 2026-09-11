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
class HPEStorageException(Exception):
	"""Exception for HPE Storage operations."""
	pass


class CpgDoesNotExist(HPEStorageException):
	"""Raised when attempting to access a CPG that does not exist."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"CPG '{name}' does not exist."
		super().__init__(self.message)

class CpgAlreadyExists(HPEStorageException):
	"""Raised when attempting to create a CPG that already exists."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"CPG '{name}' already exists."
		super().__init__(self.message)

class VolumeDoesNotExist(HPEStorageException):
	"""Raised when attempting to access a volume that does not exist."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Volume '{name}' does not exist."
		super().__init__(self.message)

class VolumeAlreadyExists(HPEStorageException):
	"""Raised when attempting to create a volume that already exists."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Volume '{name}' already exists."
		super().__init__(self.message)

class AppSetDoesNotExist(HPEStorageException):
	"""Raised when attempting to access an application set that does not exist."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Application set '{name}' does not exist."
		super().__init__(self.message)

class QosDoesNotExist(HPEStorageException):
	"""Raised when attempting to access a QoS rule that does not exist."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"QoS rule '{name}' does not exist."
		super().__init__(self.message)

class QosAlreadyExists(HPEStorageException):
	"""Raised when attempting to create a QoS rule that already exists."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"QoS rule '{name}' already exists."
		super().__init__(self.message)

class ScheduleDoesNotExist(HPEStorageException):
	"""Raised when attempting to access a schedule that does not exist."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Schedule '{name}' does not exist."
		super().__init__(self.message)

class ScheduleAlreadyExists(HPEStorageException):
	"""Raised when attempting to create a schedule that already exists."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Schedule '{name}' already exists."
		super().__init__(self.message)




class VolumeSetAlreadyExists(HPEStorageException):
	"""Raised when attempting to create a volume set that already exists."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Volume set '{name}' already exists."
		super().__init__(self.message)

class VolumeSetDoesNotExist(HPEStorageException):
	"""Raised when attempting to access a volume set that does not exist."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Volume set '{name}' does not exist."
		super().__init__(self.message)

class VolumeSetMembersAlreadyPresent(HPEStorageException):
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"All specified members are already present in volume set '{name}'."
		super().__init__(self.message)

class VolumeSetMembersAlreadyRemoved(HPEStorageException):
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"All specified members are already removed from '{name}' volume set or not present."
		super().__init__(self.message)

class HostSetAlreadyExists(HPEStorageException):
	"""Raised when attempting to create a host set that already exists."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Host set '{name}' already exists."
		super().__init__(self.message)

class HostSetDoesNotExist(HPEStorageException):
	"""Raised when attempting to access a host set that does not exist."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Host set '{name}' does not exist."
		super().__init__(self.message)

class HostSetMembersAlreadyPresent(HPEStorageException):
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"All specified host members are already present in host set '{name}'."
		super().__init__(self.message)

class HostSetMembersAlreadyRemoved(HPEStorageException):
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"All specified host members are already removed from '{name}' host set or not present."
		super().__init__(self.message)

class InvalidParameterValue(HPEStorageException):
	"""Raised when provided parameters are invalid."""
	def __init__(self, param=None, message=None):
		self.param = param
		# Allow callers to pass either a full message or a short reason
		if message:
			self.message = f"Invalid parameter value provided for '{param}'. {message}"
		else:
			self.message = f"Invalid parameter value(s) provided for '{param}'"
		super().__init__(self.message)

	def __str__(self):
		return self.message

class HTTPNotFound(HPEStorageException):
	"""Raised when a requested resource was not found after creation.

	This mirrors the HTTPNotFound used by some upstream SDKs. Accepts an
	optional `error` dict or message string.
	"""
	def __init__(self, error=None):
		self.error = error
		super().__init__(str(error) if error is not None else None)


class HostAlreadyExists(HPEStorageException):
	"""Raised when attempting to create a host that already exists."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Host '{name}' already exists."
		super().__init__(self.message)

class HostDoesNotExist(HPEStorageException):
	"""Raised when attempting to access a host that does not exist."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Host '{name}' does not exist."
		super().__init__(self.message)

class InvalidInput(HPEStorageException):
	"""Raised when input parameters are invalid or missing."""
	def __init__(self, message=None):
		self.message = message or "Invalid input provided."
		super().__init__(self.message)


class SystemDoesNotExist(HPEStorageException):
	"""Raised when attempting to access a system that does not exist."""
	def __init__(self, system_uid=None, message=None):
		self.system_uid = system_uid
		self.message = message or f"System '{system_uid}' does not exist."
		super().__init__(self.message)


# HTTPError for precise HTTP error handling
class HTTPError(HPEStorageException):
	"""HTTP error with status code and message.

	Carries the HTTP status code to allow precise error handling upstream.
	"""
	def __init__(self, status_code, message=None):
		self.status_code = status_code
		self.message = message or "HTTP error"
		super().__init__(f"HTTP {status_code}: {self.message}")


class UserAlreadyExists(HPEStorageException):
	"""Raised when attempting to create a user that already exists."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"User '{name}' already exists."
		super().__init__(self.message)


class UserDoesNotExist(HPEStorageException):
	"""Raised when attempting to access a user that does not exist."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"User '{name}' does not exist."
		super().__init__(self.message)


class CertificateDoesNotExist(HPEStorageException):
	"""Raised when attempting to access a certificate that does not exist."""
	def __init__(self, uid=None, message=None):
		self.uid = uid
		self.message = message or f"Certificate '{uid}' does not exist."
		super().__init__(self.message)


class CertificateAlreadyExists(HPEStorageException):
	"""Raised when attempting to create a certificate that already exists."""
	def __init__(self, uid=None, message=None):
		self.uid = uid
		self.message = message or f"Certificate '{uid}' already exists."
		super().__init__(self.message)


class AuthenticationError(HPEStorageException):
	"""Raised when authentication fails or insufficient privileges."""
	def __init__(self, message=None):
		self.message = message or "Authentication failed or insufficient privileges."
		super().__init__(self.message)


class RemoteCopyGroupDoesNotExist(HPEStorageException):
	"""Raised when attempting to access a remote copy group that does not exist."""
	def __init__(self, name=None, message=None):
		self.name = name
		self.message = message or f"Remote copy group '{name}' does not exist."
		super().__init__(self.message)


