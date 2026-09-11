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
"""Validator for certificate-related parameters."""

import re
from hpe_storage_flowkit_py.v3.core import exceptions

# Valid certificate types (as per API documentation)
VALID_CERT_TYPES = ['selfsigned', 'csr', 'import']

# Valid key sizes for certificates
VALID_KEY_SIZES = [2048, 3072, 4096]

# Valid SSL service names
VALID_SSL_SERVICES = ['cim', 'cli', 'dscc', 'ekm-client', 'ekm-server', 'ldap', 'qw-client', 
                      'qw-server', 'syslog-gen-client', 'syslog-gen-server', 'syslog-sec-client', 
                      'syslog-sec-server', 'wsapi', 'unified-server']

# Certificate defaults
DEFAULT_KEY_SIZE = 2048
DEFAULT_DAYS = 1095
MIN_DAYS = 1
MAX_DAYS = 3650


def validate_certificate_params(uid=None, cert_name=None, service=None, cert_type=None, common_name=None, 
                                key_length=None, days=None, authority_chain=None, 
                                certificate=None, subject_alt=None, **kwargs):
    """Validate certificate parameters.
    
    Args:
        uid (str): Certificate UID for operations requiring it
        cert_name (str): Certificate name for identification
        service (str): Service name for certificate (used in create operations)
        cert_type (str): Type of certificate (selfsigned, csr, import, etc.)
        common_name (str): Common name for certificate
        key_length (int): Key length for certificate
        days (int): Number of days certificate should be valid
        authority_chain (str): Authority chain for import type certificates
        certificate (str): Certificate content for import type
        subject_alt (str): Subject alternative name
        
    Raises:
        exceptions.InvalidInput: If validation fails
    """
    
    # Validate certificate UID (for operations requiring it)
    if uid is not None:
        if not isinstance(uid, str):
            raise exceptions.InvalidInput("Certificate UID must be a string")
        
        if not uid.strip():
            raise exceptions.InvalidInput("Certificate UID cannot be empty")
    
    # Validate certificate name (for operations requiring it)
    if cert_name is not None:
        if not isinstance(cert_name, str):
            raise exceptions.InvalidInput("Certificate name must be a string")
        
        if not cert_name.strip():
            raise exceptions.InvalidInput("Certificate name cannot be empty")
    
    # Validate service name
    if service is not None:
        if not isinstance(service, str):
            raise exceptions.InvalidInput("Service must be a string")
        
        if not service.strip():
            raise exceptions.InvalidInput("Service name cannot be empty")
        
        if service not in VALID_SSL_SERVICES:
            raise exceptions.InvalidInput(f"SSL service must be one of: {', '.join(VALID_SSL_SERVICES)}")
    
    # Validate certificate type
    if cert_type is not None:
        if not isinstance(cert_type, str):
            raise exceptions.InvalidInput("Certificate type must be a string")
        
        if cert_type not in VALID_CERT_TYPES:
            raise exceptions.InvalidInput(f"Certificate type must be one of: {', '.join(VALID_CERT_TYPES)}")
    
    # Validate common name
    if common_name is not None:
        if not isinstance(common_name, str):
            raise exceptions.InvalidInput("Common name must be a string")
        
        if not common_name.strip():
            raise exceptions.InvalidInput("Common name cannot be empty")
        
        # Basic validation for common name format
        if len(common_name) > 64:
            raise exceptions.InvalidInput("Common name cannot exceed 64 characters")
    
    # Validate key length
    if key_length is not None:
        if not isinstance(key_length, int):
            raise exceptions.InvalidInput("Key length must be an integer")
        
        if key_length not in VALID_KEY_SIZES:
            raise exceptions.InvalidInput(f"Key length must be one of: {VALID_KEY_SIZES}. Defaults to {DEFAULT_KEY_SIZE}")
    
    # Validate days
    if days is not None:
        if not isinstance(days, int):
            raise exceptions.InvalidInput("Days must be an integer")
        
        if days < MIN_DAYS or days > MAX_DAYS:
            raise exceptions.InvalidInput(f"Days must be between {MIN_DAYS} and {MAX_DAYS}. Defaults to {DEFAULT_DAYS}")
    
    # Validate authority chain for import certificates
    if authority_chain is not None:
        if not isinstance(authority_chain, str):
            raise exceptions.InvalidInput("Authority chain must be a string")
        
        if not authority_chain.strip():
            raise exceptions.InvalidInput("Authority chain cannot be empty")
        
        # Basic PEM format validation
        if "-----BEGIN CERTIFICATE-----" not in authority_chain:
            raise exceptions.InvalidInput("Authority chain must be in PEM format")
    
    # Validate certificate content for import certificates
    if certificate is not None:
        if not isinstance(certificate, str):
            raise exceptions.InvalidInput("Certificate must be a string")
        
        if not certificate.strip():
            raise exceptions.InvalidInput("Certificate cannot be empty")
        
        # Basic PEM format validation
        if "-----BEGIN CERTIFICATE-----" not in certificate:
            raise exceptions.InvalidInput("Certificate must be in PEM format")
    
    # Validate subject alternative name
    if subject_alt is not None:
        if not isinstance(subject_alt, str):
            raise exceptions.InvalidInput("Subject alternative name must be a string")
        
        if not subject_alt.strip():
            raise exceptions.InvalidInput("Subject alternative name cannot be empty")
        
        # SAN validation - supported prefixes per documentation: DNS, email, IP, RID, URI
        valid_san_prefixes = ('DNS:', 'email:', 'IP:', 'RID:', 'URI:')
        san_parts = [part.strip() for part in subject_alt.split(',')]
        for san_part in san_parts:
            if not san_part.startswith(valid_san_prefixes):
                raise exceptions.InvalidInput(
                    f"Subject alternative name entries must start with one of: {', '.join(valid_san_prefixes)}"
                )


def validate_create_certificate_params(cert_type, service, common_name=None, key_length=None,
                                       days=None, authority_chain=None, certificate=None, **kwargs):
    """Validate parameters for certificate creation.
    
    Args:
        cert_type (str): Type of certificate to create
        service (str): Service name
        common_name (str): Common name (required for selfsigned and csr)
        key_length (int): Key length
        days (int): Validity period in days (for selfsigned)
        authority_chain (str): Authority chain (for import)
        certificate (str): Certificate content (for import)
        
    Raises:
        exceptions.InvalidInput: If validation fails
    """
    # Basic parameter validation
    validate_certificate_params(
        service=service, cert_type=cert_type, common_name=common_name,
        key_length=key_length, days=days, authority_chain=authority_chain,
        certificate=certificate, **kwargs
    )
    
    # Type-specific validation based on API specification
    if cert_type == 'selfsigned':
        if not common_name:
            raise exceptions.InvalidInput("Common name is required for self-signed certificates")
        # keyLength and days are optional for selfsigned type
    
    elif cert_type == 'csr':
        if not common_name:
            raise exceptions.InvalidInput("Common name is required for CSR certificates")
        # keyLength is optional for csr type
    
    elif cert_type == 'import':
        if not authority_chain:
            raise exceptions.InvalidInput("Authority chain is required for import certificates")
        
        if not certificate:
            raise exceptions.InvalidInput("Certificate is required for import certificates")


def validate_patch_certificate_params(authority_chain=None, certificate=None, **kwargs):
    """Validate parameters for certificate patching (finishing CSR).
    
    Args:
        authority_chain (str): Authority chain
        certificate (str): Certificate content
        
    Raises:
        exceptions.InvalidInput: If validation fails
    """
    # At least one parameter is required
    if not any([authority_chain, certificate]):
        raise exceptions.InvalidInput("At least one parameter required for certificate update")
    
    # Validate authority chain if provided
    if authority_chain is not None:
        validate_certificate_params(authority_chain=authority_chain)
    
    # Validate certificate if provided
    if certificate is not None:
        validate_certificate_params(certificate=certificate)


def validate_certificate_uid(uid, context="operation"):
    """Validate certificate UID for operations requiring it.
    
    Args:
        uid (str): Certificate UID
        context (str): Context for error messages
        
    Raises:
        exceptions.InvalidInput: If UID is invalid
    """
    if uid is None:
        raise exceptions.InvalidInput(f"Certificate UID is required for {context}")
    
    if not isinstance(uid, str):
        raise exceptions.InvalidInput("Certificate UID must be a string")
    
    if not uid.strip():
        raise exceptions.InvalidInput("Certificate UID cannot be empty")


def validate_create_payload(payload):
    """Validate certificate creation payload has required content.
    
    Args:
        payload (dict): The payload to validate
        
    Raises:
        exceptions.InvalidInput: If payload is invalid
    """
    if not payload:
        raise exceptions.InvalidInput("Certificate creation payload cannot be empty")
    
    if not isinstance(payload, dict):
        raise exceptions.InvalidInput("Certificate creation payload must be a dictionary")
    
    # Required fields
    required_fields = ['type', 'service']
    for field in required_fields:
        if field not in payload:
            raise exceptions.InvalidInput(f"Required field '{field}' missing from payload")


def validate_patch_payload(payload):
    """Validate certificate patch payload has required content.
    
    Args:
        payload (dict): The payload to validate
        
    Raises:
        exceptions.InvalidInput: If payload is invalid
    """
    if not payload:
        raise exceptions.InvalidInput("Certificate patch payload cannot be empty")
    
    if not isinstance(payload, dict):
        raise exceptions.InvalidInput("Certificate patch payload must be a dictionary")
    
    # At least one field should be present for patch
    valid_fields = ['authorityChain', 'certificate']
    if not any(field in payload for field in valid_fields):
        raise exceptions.InvalidInput(
            f"At least one of the following fields must be present: {', '.join(valid_fields)}"
        )