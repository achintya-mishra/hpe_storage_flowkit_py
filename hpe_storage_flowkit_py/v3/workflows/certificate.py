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
"""Certificate workflow implementation for HPE Alletra MP storage systems.

This module provides certificate management operations:
  - Get all certificates (GET /api/v3/certificates)
  - Get single certificate by UID (GET /api/v3/certificates/{uid})
  - Create new certificates (POST /api/v3/certificates)
  - Update/finish CSR certificates (PATCH /api/v3/certificates/{uid})
  - Delete certificates (DELETE /api/v3/certificates/{uid})

All operations use certificate UIDs for direct API calls.

Special Handling for Service Restarts:
  For selfsigned certificate creation and all certificate deletions (selfsigned, csr, import),
  the unified-server and other services automatically restart (CIM, WSAPI, UI services). This 
  causes the normal task tracking to fail because services become unavailable. The workflow 
  includes special handling that:
  - Shows a user-friendly message about the service restart
  - Returns success immediately without waiting for service restart completion
  Note: CSR and import certificate creation operations do NOT trigger service restarts.

Return convention:
  On success: raw RESTClient parsed response
  On failure: raises appropriate exception
"""

from hpe_storage_flowkit_py.v3.core import exceptions
from hpe_storage_flowkit_py.v3.core.session import SessionManager
import logging
from hpe_storage_flowkit_py.v3.workflows.task import TaskManager
from hpe_storage_flowkit_py.v3.validators.certificate_validator import (
    validate_certificate_params, validate_create_certificate_params,
    validate_patch_certificate_params, validate_certificate_uid,
    validate_create_payload, validate_patch_payload
)
from hpe_storage_flowkit_py.v3.utils.utils import handle_async_response

# HTTP Status Code Constants
HTTP_NOT_FOUND = 404
HTTP_BAD_REQUEST = 400
HTTP_CONFLICT = 409
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403

logger = logging.getLogger('flowkit')


class CertificateWorkflow:
    """Workflow for certificate operations.

    Success path returns underlying REST response (or None when API returns no body).
    Non-changed idempotent situations raise specific exceptions that the Ansible
    module maps to an unchanged result.
    """

    def __init__(self, session_mgr: SessionManager, task_manager: TaskManager):
        self.session_mgr = session_mgr
        self.task_manager = task_manager

    def _get_response_resource_uri(self, response, default_resource_uri):
        """Safely extract a resource URI from a response that may be empty."""
        if isinstance(response, dict):
            return response.get('resourceUri', default_resource_uri)
        return default_resource_uri

    def _build_create_certificate_payload(self, cert_type, service, common_name=None, 
                                           key_length=None, days=None, country=None, province=None,
                                           locality=None, organization=None, organization_unit=None,
                                           subject_alt=None, authority_chain=None, certificate=None):
        """Build payload for certificate creation (POST /api/v3/certificates).
        
        Args:
            cert_type (str): Type of certificate (selfsigned, csr, import, etc.)
            service (str): Service name
            common_name (str): Common name for certificate
            key_length (int): Key length for certificate
            days (int): Number of days certificate should be valid
            country (str): Country for certificate
            province (str): Province/state for certificate
            locality (str): Locality/city for certificate
            organization (str): Organization for certificate
            organization_unit (str): Organization unit for certificate
            subject_alt (str): Subject alternative name
            authority_chain (str): Authority chain (for import certificates)
            certificate (str): Certificate content (for import certificates)
            
        Returns:
            dict: API payload
        """
        logger.debug(f"Building certificate create payload for type '{cert_type}', service '{service}'")
        
        payload = {
            "type": cert_type,
            "service": service
        }
        
        # Add optional fields based on certificate type and provided values
        if common_name:
            payload["commonName"] = common_name
        
        if key_length:
            payload["keyLength"] = key_length
        
        if days and cert_type == 'selfsigned':
            payload["days"] = days
        
        if country:
            payload["country"] = country
        
        if province:
            payload["province"] = province
        
        if locality:
            payload["locality"] = locality
        
        if organization:
            payload["organization"] = organization
        
        if organization_unit:
            payload["organizationUnit"] = organization_unit
        
        if subject_alt:
            payload["subjectAlt"] = subject_alt
        
        # For import certificates
        if cert_type == 'import':
            if authority_chain:
                payload["authorityChain"] = authority_chain
            if certificate:
                payload["certificate"] = certificate
        
        logger.debug(f"Built create payload for certificate type '{cert_type}', service '{service}'")
        return payload

    def _build_patch_certificate_payload(self, authority_chain=None, certificate=None):
        """Build payload for certificate patching (PATCH /api/v3/certificates/{uid}).
        
        Args:
            authority_chain (str): Authority chain for the certificate
            certificate (str): Certificate content
            
        Returns:
            dict: API payload
        """
        logger.debug("Building certificate patch payload")
        payload = {}
        
        if authority_chain:
            payload["authorityChain"] = authority_chain
        
        if certificate:
            payload["certificate"] = certificate
        
        logger.debug("Built patch payload for certificate")
        return payload

    def _parse_certificates_response(self, certificates_response):
        """Parse certificates API response into list of certificate dicts."""
        if isinstance(certificates_response, dict):
            if 'members' in certificates_response and certificates_response['members']:
                return list(certificates_response['members'].values())
            elif 'uid' in certificates_response:
                return [certificates_response]
        elif isinstance(certificates_response, list):
            return certificates_response
        return []

    def _execute_get_all_certificates(self):
        """Execute get all certificates operation."""
        logger.info("Getting all certificates")
        
        try:
            endpoint = "/certificates"
            logger.info(f"Making GET request to {endpoint}")
            response = self.session_mgr.rest_client.get(endpoint)
            logger.info("Successfully retrieved all certificates")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get all certificates: {str(e)}")
            
            if hasattr(e, 'status_code'):
                status = getattr(e, 'status_code')
                if status == HTTP_UNAUTHORIZED:
                    raise exceptions.AuthenticationError("Authentication failed")
                elif status == HTTP_FORBIDDEN:
                    raise exceptions.AuthenticationError("Insufficient privileges")
            
            raise exceptions.HPEStorageException(f"Failed to get all certificates: {str(e)}")

    def get_all_certificates(self):
        """Get all certificates (GET /api/v3/certificates)."""
        logger.info(">>>>>>>Entered get_all_certificates")
        try:
            return self._execute_get_all_certificates()
        except Exception as e:
            logger.exception(f"Failed to get all certificates due to error: {e}")
            raise
        finally:
            logger.info("<<<<<<<Exited get_all_certificates")

    def _execute_get_certificate_by_uid(self, uid):
        """Execute get certificate by UID operation."""
        logger.info(f"Getting certificate '{uid}' by UID")
        
        validate_certificate_uid(uid, "get operation")
        
        try:
            endpoint = f"/certificates/{uid}"
            logger.info(f"Making GET request to {endpoint}")
            response = self.session_mgr.rest_client.get(endpoint)
            logger.info(f"Successfully retrieved certificate '{uid}'")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get certificate '{uid}': {str(e)}")
            
            if hasattr(e, 'status_code'):
                status = getattr(e, 'status_code')
                if status == HTTP_NOT_FOUND:
                    raise exceptions.CertificateDoesNotExist(f"Certificate '{uid}' not found")
                elif status == HTTP_UNAUTHORIZED:
                    raise exceptions.AuthenticationError("Authentication failed")
                elif status == HTTP_FORBIDDEN:
                    raise exceptions.AuthenticationError("Insufficient privileges")
            
            raise exceptions.HPEStorageException(f"Failed to get certificate: {str(e)}")

    def get_certificate_by_uid(self, uid):
        """Get certificate by UID (GET /api/v3/certificates/{uid})."""
        logger.info(f">>>>>>>Entered get_certificate_by_uid: uid='{uid}'")
        try:
            return self._execute_get_certificate_by_uid(uid)
        except Exception as e:
            logger.exception(f"Failed to get certificate by UID due to error: {e}")
            raise
        finally:
            logger.info(f"<<<<<<<Exited get_certificate_by_uid: uid='{uid}'")

    def _handle_selfsigned_certificate_creation(self, service, response):
        """Handle special case for selfsigned certificate creation that causes service restarts.
        
        Args:
            service (str): Service name for the certificate
            response (dict): API response from certificate creation
            
        Returns:
            dict: Success result with certificate information
        """
        logger.info("Self-signed certificate creation detected. Services will restart.")
        
        # Show the service restart message to user
        restart_message = (
            "Self-signed certificate created.\n"
            "Web Services API server and HPE Alletra Storage UI stopped successfully.\n"
            "The Web Services API server and HPE Alletra Storage UI will start shortly."
        )
        print(restart_message)
        logger.info(restart_message)
        
        # Return success immediately without waiting or validation
        logger.info(f"Certificate creation completed for service '{service}' - services restarting")
        return {
            'message': 'Operation successful', 
            'resourceUri': self._get_response_resource_uri(response, '/api/v3/certificates'),
            'status': 'Certificate created - services restarting'
        }
        
    def _execute_create_certificate(self, cert_type, service, common_name=None, key_length=None, 
                                    days=None, country=None, province=None, locality=None,
                                    organization=None, organization_unit=None, subject_alt=None,
                                    authority_chain=None, certificate=None, **kwargs):
        """Execute create certificate operation."""
        logger.info(f"Starting certificate creation for service '{service}', type '{cert_type}'")
        
        # Validate create parameters
        validate_create_certificate_params(
            cert_type=cert_type, service=service, common_name=common_name,
            key_length=key_length, days=days, authority_chain=authority_chain,
            certificate=certificate, **kwargs
        )
        
        payload = self._build_create_certificate_payload(
            cert_type=cert_type, service=service, common_name=common_name,
            key_length=key_length, days=days, country=country, province=province,
            locality=locality, organization=organization, organization_unit=organization_unit,
            subject_alt=subject_alt, authority_chain=authority_chain, certificate=certificate
        )
        
        validate_create_payload(payload)
        
        logger.info(f"Creating certificate for service '{service}' with type '{cert_type}'")
        response = self.session_mgr.rest_client.post("/certificates", payload)
        
        # Special handling for selfsigned certificates that cause service restarts
        if cert_type == 'selfsigned':
            logger.info("Detected selfsigned certificate creation - using special restart handling")
            result = self._handle_selfsigned_certificate_creation(service, response)
        else:
            result = handle_async_response(self.task_manager, "certificate creation", 
                                           f"{service}:{cert_type}", response)
        
        logger.info(f"Certificate for service '{service}' created successfully")
        return result

    def create_certificate(self, cert_type, service, common_name=None, key_length=None, days=None,
                          country=None, province=None, locality=None, organization=None,
                          organization_unit=None, subject_alt=None, authority_chain=None,
                          certificate=None, **kwargs):
        """Create a new certificate (POST /api/v3/certificates).
        
        Performs comprehensive validation before sending the request:
        - Validates required parameters for the operation
        - Validates type-specific requirements
        - Builds and validates the API payload
        """
        logger.info(f">>>>>>>Entered create_certificate: service='{service}', type='{cert_type}'")
        try:
            # Operation-specific validations (moved from Ansible module)
            if not cert_type:
                raise exceptions.InvalidParameterValue("cert_type is required for create operation")
            if not service:
                raise exceptions.InvalidParameterValue("service is required for create operation")
            
            # Type-specific validations (based on API specification)
            if cert_type == 'selfsigned':
                if not common_name:
                    raise exceptions.InvalidParameterValue("common_name is required for selfsigned certificates")
                # keyLength and days are optional for selfsigned type
            
            elif cert_type == 'csr':
                if not common_name:
                    raise exceptions.InvalidParameterValue("common_name is required for CSR certificates")
                # keyLength is optional for csr type
            
            elif cert_type == 'import':
                if not authority_chain:
                    raise exceptions.InvalidParameterValue("authority_chain is required for import certificates")
                if not certificate:
                    raise exceptions.InvalidParameterValue("certificate is required for import certificates")
            
            return self._execute_create_certificate(
                cert_type=cert_type, service=service, common_name=common_name,
                key_length=key_length, days=days, country=country, province=province,
                locality=locality, organization=organization, organization_unit=organization_unit,
                subject_alt=subject_alt, authority_chain=authority_chain,
                certificate=certificate, **kwargs
            )
        except Exception as e:
            logger.exception(f"Failed to create certificate due to error: {e}")
            raise
        finally:
            logger.info(f"<<<<<<<Exited create_certificate: service='{service}', type='{cert_type}'")

    def _execute_patch_certificate(self, uid, authority_chain=None, certificate=None, **kwargs):
        """Execute patch certificate operation."""
        logger.info(f"Starting certificate patch for UID '{uid}'")
        
        validate_certificate_uid(uid, "patch operation")
        validate_patch_certificate_params(
            authority_chain=authority_chain, certificate=certificate, **kwargs
        )
        
        payload = self._build_patch_certificate_payload(
            authority_chain=authority_chain, certificate=certificate
        )
        
        validate_patch_payload(payload)
        
        logger.info(f"Patching certificate '{uid}'")
        endpoint = f"/certificates/{uid}"
        logger.debug(f"Making PATCH request to {endpoint}")
        response = self.session_mgr.rest_client.patch(endpoint, payload)
        result = handle_async_response(self.task_manager, "certificate patch", uid, response)
        logger.info(f"Certificate '{uid}' patched successfully")
        return result

    def patch_certificate(self, uid, authority_chain=None, certificate=None, **kwargs):
        """Patch certificate (PATCH /api/v3/certificates/{uid})."""
        logger.info(f">>>>>>>Entered patch_certificate: uid='{uid}'")
        try:
            return self._execute_patch_certificate(
                uid=uid, authority_chain=authority_chain, certificate=certificate,
                **kwargs
            )
        except Exception as e:
            logger.exception(f"Failed to patch certificate due to error: {e}")
            raise
        finally:
            logger.info(f"<<<<<<<Exited patch_certificate: uid='{uid}'")

    def _handle_certificate_deletion(self, identifier, response, cert_type=''):
        """Handle certificate deletion response.
        
        All certificate deletions cause services to restart, so we return
        immediately without waiting for task completion and show a restart notice.
        
        Args:
            identifier (str): Certificate UID or name being deleted
            response (dict): API response from certificate deletion
            cert_type (str): Type of certificate being deleted
            
        Returns:
            dict: Success result with certificate information
        """
        logger.info(f"Certificate deletion detected for '{identifier}' (type: '{cert_type}'). Services will restart.")
        
        restart_message = (
            "Certificates removed.\n"
            "Web Services API server and HPE Alletra Storage UI stopped successfully.\n"
            "The Web Services API server and HPE Alletra Storage UI will start shortly."
        )
        print(restart_message)
        logger.info(restart_message)
        logger.info(f"Certificate deletion completed for '{identifier}' - services restarting")
        
        return {
            'message': 'Operation successful',
            'resourceUri': self._get_response_resource_uri(response, '/api/v3/certificates'),
            'status': 'Certificate deleted - services restarting'
        }

    def _execute_delete_certificate(self, uid):
        """Execute delete certificate operation."""
        logger.info(f"Starting certificate deletion for UID '{uid}'")
        
        validate_certificate_uid(uid, "delete operation")
        
        # Fetch the certificate to determine its type before deletion
        cert_info = self._execute_get_certificate_by_uid(uid)
        cert_type = cert_info.get('type', '') if isinstance(cert_info, dict) else ''
        
        logger.info(f"Deleting certificate '{uid}' (type: '{cert_type}')")
        endpoint = f"/certificates/{uid}"
        logger.debug(f"Making DELETE request to {endpoint}")
        response = self.session_mgr.rest_client.delete(endpoint)
        result = self._handle_certificate_deletion(uid, response, cert_type)
        logger.info(f"Certificate '{uid}' deleted successfully")
        return result

    def delete_certificate(self, uid):
        """Delete certificate (DELETE /api/v3/certificates/{uid})."""
        logger.info(f">>>>>>>Entered delete_certificate: uid='{uid}'")
        try:
            return self._execute_delete_certificate(uid)
        except Exception as e:
            logger.exception(f"Failed to delete certificate due to error: {e}")
            raise
        finally:
            logger.info(f"<<<<<<<Exited delete_certificate: uid='{uid}'")

    # ---- Name-based operations for certificate identification ----

    def _find_certificates_by_name(self, cert_name):
        """Find all certificates that match a given common name."""
        certificates_response = self.session_mgr.rest_client.get("/certificates")
        certificates_list = self._parse_certificates_response(certificates_response)
        return [
            cert for cert in certificates_list
            if isinstance(cert, dict) and cert.get('commonname') == cert_name
        ]

    def _fetch_certificate_uid_by_name(self, cert_name):
        """Fetch certificate UID and type by certificate name for modify/delete operations.
        
        Args:
            cert_name (str): Certificate name to lookup
            
        Returns:
            tuple: (uid, cert_type) - Certificate UID and type
            
        Raises:
            exceptions.CertificateDoesNotExist: If certificate with name is not found
            exceptions.HPEStorageException: For other API errors
        """
        try:
            logger.debug(f"Fetching UID for certificate name '{cert_name}'")

            matching_certificates = self._find_certificates_by_name(cert_name)

            if len(matching_certificates) > 1:
                raise exceptions.InvalidInput(
                    f"Multiple certificates with name '{cert_name}' found; use a unique certificate name"
                )

            if matching_certificates:
                cert = matching_certificates[0]
                uid = cert.get('uid')
                cert_type = cert.get('type', '')
                validate_certificate_uid(uid, cert_name)
                logger.debug(f"Found UID '{uid}', type '{cert_type}' for certificate name '{cert_name}'")
                return uid, cert_type

            raise exceptions.CertificateDoesNotExist(f"Certificate with name '{cert_name}' not found")
            
        except exceptions.CertificateDoesNotExist:
            raise
        except exceptions.InvalidInput:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch UID for certificate name '{cert_name}': {str(e)}")
            raise exceptions.HPEStorageException(f"Failed to fetch certificate UID: {str(e)}")

    def _execute_get_certificate_by_name(self, cert_name):
        """Execute get certificate by name operation."""
        logger.info(f"Getting certificate with name '{cert_name}'")
        
        # For get operations, cert_name is required
        if cert_name is None:
            raise exceptions.InvalidInput("Certificate name is required")
        
        validate_certificate_params(cert_name=cert_name)
        
        matching_certificates = self._find_certificates_by_name(cert_name)

        if len(matching_certificates) > 1:
            raise exceptions.InvalidInput(
                f"Multiple certificates with name '{cert_name}' found; use a unique certificate name"
            )

        if matching_certificates:
            cert = matching_certificates[0]
            logger.debug(f"Found certificate with name '{cert_name}' and UID '{cert.get('uid')}'")
            return cert

        raise exceptions.CertificateDoesNotExist(f"Certificate with name '{cert_name}' not found")

    def get_certificate_by_name(self, cert_name):
        """Get certificate by name (searches all certificates efficiently)."""
        logger.info(f">>>>>>>Entered get_certificate_by_name: cert_name='{cert_name}'")
        try:
            return self._execute_get_certificate_by_name(cert_name)
        except Exception as e:
            logger.exception(f"Failed to get certificate by name due to error: {e}")
            raise
        finally:
            logger.info(f"<<<<<<<Exited get_certificate_by_name: cert_name='{cert_name}'")

    def _execute_delete_certificate_by_name(self, cert_name):
        """Execute delete certificate by name operation."""
        logger.info(f"Starting certificate deletion for name '{cert_name}'")
        
        # For delete operations, cert_name is required
        if cert_name is None:
            raise exceptions.InvalidInput("Certificate name is required for deletion")
        
        validate_certificate_params(cert_name=cert_name)
        
        # Fetch UID and type (will raise CertificateDoesNotExist if certificate doesn't exist)
        uid, cert_type = self._fetch_certificate_uid_by_name(cert_name)
        logger.info(f"Found UID '{uid}', type '{cert_type}' for certificate name '{cert_name}'")
        
        logger.info(f"Deleting certificate with name '{cert_name}'")
        endpoint = f"/certificates/{uid}"
        logger.debug(f"Making DELETE request to {endpoint}")
        response = self.session_mgr.rest_client.delete(endpoint)
        result = self._handle_certificate_deletion(cert_name, response, cert_type)
        logger.info(f"Certificate with name '{cert_name}' deleted successfully")
        return result

    def delete_certificate_by_name(self, cert_name):
        """Delete certificate by name (internally converts name to UID)."""
        logger.info(f">>>>>>>Entered delete_certificate_by_name: cert_name='{cert_name}'")
        try:
            return self._execute_delete_certificate_by_name(cert_name)
        except Exception as e:
            logger.exception(f"Failed to delete certificate due to error: {e}")
            raise
        finally:
            logger.info(f"<<<<<<<Exited delete_certificate_by_name: cert_name='{cert_name}'")

    def _execute_patch_certificate_by_name(self, cert_name, authority_chain=None, certificate=None, **kwargs):
        """Execute patch certificate by name operation."""
        logger.info(f"Starting certificate patching for name '{cert_name}'")
        
        # For patch operations, cert_name is required
        if cert_name is None:
            raise exceptions.InvalidInput("Certificate name is required for patch")
        
        validate_certificate_params(cert_name=cert_name)
        validate_patch_certificate_params(authority_chain, certificate)
        
        payload = self._build_patch_certificate_payload(authority_chain, certificate)
        validate_patch_payload(payload)
        
        # Fetch UID (will raise CertificateDoesNotExist if certificate doesn't exist)
        uid, _ = self._fetch_certificate_uid_by_name(cert_name)
        logger.info(f"Found UID '{uid}' for certificate name '{cert_name}'")
        
        logger.info(f"Patching certificate with name '{cert_name}'")
        endpoint = f"/certificates/{uid}"
        logger.debug(f"Making PATCH request to {endpoint}")
        response = self.session_mgr.rest_client.patch(endpoint, payload)
        
        # Certificate patch triggers a service restart, which may cause task polling
        # to fail with connection errors (SSL EOF, connection reset, etc.).
        # Since the PATCH was already accepted by the array, treat task polling
        # failures as success.
        try:
            result = handle_async_response(self.task_manager, "certificate patching", cert_name, response)
        except Exception as e:
            logger.warning(
                f"Task polling failed during certificate patch (likely due to service restart): {e}. "
                f"The PATCH request was accepted by the array — treating as success."
            )
            result = None
        
        logger.info(f"Certificate with name '{cert_name}' patched successfully")
        return result

    def patch_certificate_by_name(self, cert_name, authority_chain=None, certificate=None, **kwargs):
        """Patch certificate by name (internally converts name to UID).
        
        Validates that the cert_name parameter and at least one patch parameter is provided.
        """
        logger.info(f">>>>>>>Entered patch_certificate_by_name: cert_name='{cert_name}'")
        try:
            # Operation-specific validations (moved from Ansible module)
            if not cert_name:
                raise exceptions.InvalidParameterValue("Certificate name is required for patch operation")
            
            if not any([authority_chain, certificate]):
                raise exceptions.InvalidParameterValue("At least one of authority_chain or certificate is required for patch operation")
            
            return self._execute_patch_certificate_by_name(cert_name, authority_chain, certificate, **kwargs)
        except Exception as e:
            logger.exception(f"Failed to patch certificate due to error: {e}")
            raise
        finally:
            logger.info(f"<<<<<<<Exited patch_certificate_by_name: cert_name='{cert_name}'")