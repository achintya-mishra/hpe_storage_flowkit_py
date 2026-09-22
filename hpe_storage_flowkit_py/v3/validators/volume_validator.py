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
import logging

logger = logging.getLogger('flowkit')

def validate_create_volume_params(name, sizeMiB, userCpg, params=None):
	"""
	Validate parameters for volume creation.
	
	Args:
		name (str): Name of the volume to be created (required)
		sizeMiB (int): Size of the volume to be created in MiB (required, min=1)
		userCpg (str): User CPG of the volume to be created (required)
		params (dict): Optional parameters for volume creation
			
	Allowed optional parameters:
		- comments (str): Comments of the volume
		- count (int): Count of volumes to be created (positive int)
		- dataReduction (bool): Data reduction setting
		- expireSecs (int): Expiration value for volume snapshot (uint64)
		- keyValuePairs (dict): Key value pairs assigned to the object
		- ransomWare (bool): Enable/disable ransomware policy
		- retainSecs (int): Retention value for volume snapshot (uint64)
		- userAllocWarning (int): User allocation warning (0-100)
	
	Raises:
		ValueError: If validation fails
	"""
	logger.info("Started validating create volume parameters")
	# Validate required parameters
	if not name or not isinstance(name, str):
		raise ValueError("Volume name must be a non-empty string")
	
	if not isinstance(sizeMiB, int) or sizeMiB < 1:
		raise ValueError("sizeMiB must be a positive integer (minimum 1 MiB)")
	
	if not userCpg or not isinstance(userCpg, str):
		raise ValueError("userCpg must be a non-empty string")
	
	# Define allowed optional parameters
	ALLOWED_PARAMS = {
		'comments', 'count', 'dataReduction', 'expireSecs', 
		'keyValuePairs', 'ransomWare', 'retainSecs', 'userAllocWarning'
	}
	
	if params is None:
		return
	
	if not isinstance(params, dict):
		raise ValueError("params must be a dictionary")
	
	# Check for unknown parameters
	unknown_params = set(params.keys()) - ALLOWED_PARAMS
	if unknown_params:
		raise ValueError(f"Unknown parameters: {', '.join(unknown_params)}. Allowed parameters: {', '.join(sorted(ALLOWED_PARAMS))}")
	
	# Validate each optional parameter
	for param, value in params.items():
		if param == 'comments':
			if not isinstance(value, str):
				raise ValueError("'comments' must be a string")
		
		elif param == 'count':
			if not isinstance(value, int) or value < 1:
				raise ValueError("'count' must be a positive integer")
		
		elif param == 'dataReduction':
			if not isinstance(value, bool):
				raise ValueError("'dataReduction' must be a boolean")
		
		elif param == 'expireSecs':
			if not isinstance(value, int) or value < 0:
				raise ValueError("'expireSecs' must be a non-negative integer (uint64)")
		
		elif param == 'keyValuePairs':
			if not isinstance(value, dict):
				raise ValueError("'keyValuePairs' must be a dictionary")
			for k, v in value.items():
				if not isinstance(k, str) or not isinstance(v, str):
					raise ValueError("'keyValuePairs' must contain string keys and string values")
		
		elif param == 'ransomWare':
			if not isinstance(value, bool):
				raise ValueError("'ransomWare' must be a boolean")
		
		elif param == 'retainSecs':
			if not isinstance(value, int) or value < 0:
				raise ValueError("'retainSecs' must be a non-negative integer (uint64)")
		
		elif param == 'userAllocWarning':
			if not isinstance(value, int) or value < 0 or value > 100:
				raise ValueError("'userAllocWarning' must be an integer between 0 and 100")
	
	logger.info("Completed validating create volume parameters")

def validate_modify_volume_params(vol_name,params=None):
	"""
	Validate parameters for volume modification.
	
	Args:
		params (dict): Optional parameters for volume modification
			
	Allowed optional parameters:
		- comments (str): Edit comment of virtual volume
		- expireSecs (int): Expiration value for volume snapshot (uint64)
		- keyValuePairs (dict): Key value pairs assigned to the object
		- name (str): Edit name of virtual volume
		- ransomWare (bool): Enable/disable ransomware policy
		- retainSecs (int): Retention value for volume snapshot (uint64)
		- sizeMiB (float): Edit size of virtual volume (min=1)
		- userAllocWarning (int): Edit user space allocation warning (0-100)
		- wwn (str): Edit VV WWN
	
	Raises:
		ValueError: If validation fails
	"""
	logger.info("Started validating modify volume parameters")
	if not vol_name or not isinstance(vol_name, str):
		raise ValueError("Volume name must be a non-empty string")
	# Define allowed optional parameters
	ALLOWED_PARAMS = {
		'comments', 'expireSecs', 'keyValuePairs', 'name', 
		'ransomWare', 'retainSecs', 'sizeMiB', 'userAllocWarning', 'wwn'
	}
	
	if params is None:
		return
	
	if not isinstance(params, dict):
		raise ValueError("params must be a dictionary")
	
	if not params:
		raise ValueError("At least one parameter must be provided for modification")
	
	# Check for unknown parameters
	unknown_params = set(params.keys()) - ALLOWED_PARAMS
	if unknown_params:
		raise ValueError(f"Unknown parameters: {', '.join(unknown_params)}. Allowed parameters: {', '.join(sorted(ALLOWED_PARAMS))}")
	
	# Validate each optional parameter
	for param, value in params.items():
		if param == 'comments':
			if not isinstance(value, str):
				raise ValueError("'comments' must be a string")
		
		elif param == 'expireSecs':
			if not isinstance(value, int) or value < 0:
				raise ValueError("'expireSecs' must be a non-negative integer (uint64)")
		
		elif param == 'keyValuePairs':
			if not isinstance(value, dict):
				raise ValueError("'keyValuePairs' must be a dictionary")
			for k, v in value.items():
				if not isinstance(k, str) or not isinstance(v, str):
					raise ValueError("'keyValuePairs' must contain string keys and string values")
		
		elif param == 'name':
			if not isinstance(value, str) or not value:
				raise ValueError("'name' must be a non-empty string")
		
		elif param == 'ransomWare':
			if not isinstance(value, bool):
				raise ValueError("'ransomWare' must be a boolean")
		
		elif param == 'retainSecs':
			if not isinstance(value, int) or value < 0:
				raise ValueError("'retainSecs' must be a non-negative integer (uint64)")
		
		elif param == 'sizeMiB':
			if not isinstance(value, (int, float)) or value < 1:
				raise ValueError("'sizeMiB' must be a positive number (minimum 1 MiB)")
		
		elif param == 'userAllocWarning':
			if not isinstance(value, int) or value < 0 or value > 100:
				raise ValueError("'userAllocWarning' must be an integer between 0 and 100")
		
		elif param == 'wwn':
			if not isinstance(value, str) or not value:
				raise ValueError("'wwn' must be a non-empty string")
	
	logger.info("Completed validating modify volume parameters")

def validate_tune_volume_params(name,cpg,params=None):
	"""
	Validate parameters for volume tuning.
	
	Args:
		params (dict): Parameters for tune volume operation
			
	Allowed parameters:
		- conversionType (str): Change provision type of virtual volume
		  Allowed values: CONVERSIONTYPE_THIN, CONVERSIONTYPE_V1, CONVERSIONTYPE_V2
		  Default: CONVERSIONTYPE_V1
		- saveToNewName (str): Tune virtual volume and save the original under a new name
		- userCpgName (str): Change user CPG of virtual volume (required)
	
	Raises:
		ValueError: If validation fails
	"""
	logger.info("Started validating tune volume parameters")
	if not name or not isinstance(name, str):
		raise ValueError("Volume name must be a non-empty string")
	if not cpg or not isinstance(cpg, str):
		raise ValueError("Volume name must be a non-empty string")
	# Define allowed parameters
	ALLOWED_PARAMS = {
		'conversionType', 'saveToNewName', 'userCpgName'
	}
	
	# Define allowed conversion types
	ALLOWED_CONVERSION_TYPES = {
		'CONVERSIONTYPE_THIN',
		'CONVERSIONTYPE_V1', 
		'CONVERSIONTYPE_V2'
	}
	
	if params is None:
		raise ValueError("params must be provided for tune volume operation")
	
	if not isinstance(params, dict):
		raise ValueError("params must be a dictionary")
	
	if not params:
		raise ValueError("At least one parameter must be provided for tune operation")
	
	# Check for unknown parameters
	unknown_params = set(params.keys()) - ALLOWED_PARAMS
	if unknown_params:
		raise ValueError(f"Unknown parameters: {', '.join(unknown_params)}. Allowed parameters: {', '.join(sorted(ALLOWED_PARAMS))}")
	
	# Validate each parameter
	for param, value in params.items():
		if param == 'conversionType':
			if not isinstance(value, str):
				raise ValueError("'conversionType' must be a string")
			if value not in ALLOWED_CONVERSION_TYPES:
				raise ValueError(f"'conversionType' must be one of: {', '.join(sorted(ALLOWED_CONVERSION_TYPES))}")
		
		elif param == 'saveToNewName':
			if not isinstance(value, str) or not value:
				raise ValueError("'saveToNewName' must be a non-empty string")
	
	logger.info("Completed validating tune volume parameters")

def validate_volume_params(name, size=None, cpg=None):
	logger.info("Started validating volume parameters")
	if not name or not isinstance(name, str):
		raise ValueError("Volume name must be a non-empty string.")
	if size is not None and (not isinstance(size, int) or size <= 0):
		raise ValueError("Volume size must be a positive integer.")
	if cpg is not None and not isinstance(cpg, str):
		raise ValueError("CPG must be a string.")
	logger.info("Completed validating volume parameters")

