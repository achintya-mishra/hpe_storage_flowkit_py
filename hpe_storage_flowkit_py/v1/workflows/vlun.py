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

from urllib.parse import quote
from hpe_storage_flowkit_py.v1.src.core import exceptions
from hpe_storage_flowkit_py.v1.src.core.exceptions import HPEStorageException
from hpe_storage_flowkit_py.v1.src.core.session import SessionManager
from hpe_storage_flowkit_py.v1.src.validators.vlun_validator import validate_vlun_params

class VLUNWorkflow:
    """
    VLUNWorkflow
    """

    PORT_MODE_TARGET = 2
    PORT_MODE_INITIATOR = 3
    PORT_MODE_PEER = 4

    PORT_PROTO_FC = 1
    PORT_PROTO_ISCSI = 2
    PORT_PROTO_FCOE = 3
    PORT_PROTO_IP = 4
    PORT_PROTO_SAS = 5
    PORT_PROTO_NVME = 6

    PORT_STATE_READY = 4
    PORT_STATE_SYNC = 5
    PORT_STATE_OFFLINE = 10

    DEFAULT_NVME_PORT = 4420
    DEFAULT_PORT_NQN = 'nqn.2014-08.org.nvmexpress.discovery'

    def __init__(self, session_client: SessionManager):
        """
        __init__
        """
        self.session_client = session_client

    def export_volume_to_host(self, payload):
        """
        export_volume_to_host
        """
        return self.session_client.rest_client.post("/vluns", payload)

    def unexport_volume_from_host(self, vlun_id):
        """
        unexport_volume_from_host
        """
        return self.session_client.rest_client.delete(f"/vluns/{vlun_id}")

    def export_volume_to_hostset(self, payload):
        """
        export_volume_to_hostset
        """
        return self.session_client.rest_client.post("/vluns", payload)

    def unexport_volume_from_hostset(self, vlun_id):
        """
        unexport_volume_from_hostset
        """
        return self.session_client.rest_client.delete(f"/vluns/{vlun_id}")

    def export_volumeset_to_host(self, payload):
        """
        export_volumeset_to_host
        """
        return self.session_client.rest_client.post("/vluns", payload)

    def unexport_volumeset_from_host(self, vlun_id):
        """
        unexport_volumeset_from_host
        """
        return self.session_client.rest_client.delete(f"/vluns/{vlun_id}")

    def export_volumeset_to_hostset(self, payload):
        """
        export_volumeset_to_hostset
        """
        return self.session_client.rest_client.post("/vluns", payload)

    def unexport_volumeset_from_hostset(self, vlun_id):
        """
        unexport_volumeset_from_hostset
        """
        return self.session_client.rest_client.delete(f"/vluns/{vlun_id}")

    def vlun_exists(self, volume_name, lun, host_name=None, port_pos=None):
        """
        vlun_exists
        """
        vluns = self.list_vluns()
        for vlun in vluns:
            if (
                vlun.get("volumeName") == volume_name
                and vlun.get("lun") == lun
                and (host_name is None or vlun.get("hostname") == host_name)
                and (port_pos is None or vlun.get("portPos") == port_pos)
            ):
                return True
        return False

    def list_vluns(self):
        """
        list_vluns
        """
        response = self.session_client.rest_client.get("/vluns")
        if response is None:
            return []
        return response.get("members", [])

    def get_vvsets(self, volume_set_name):
        """
        get_vvsets
        """
        return self.session_client.rest_client.get(f"/volumesets/{volume_set_name}")


    # below functions reqd for cinder

    def create_vlun(self, volume_name, host_name, params):
        validate_vlun_params(volume_name, host_name, params)
        payload = {"volumeName": volume_name, "hostname": host_name}
        payload.update(params)
        try:
            response = self.session_client.rest_client.post("/vluns", payload)
            return response
        except HPEStorageException as e:
            raise

    def delete_vlun(self, volumeName, lunID, hostname=None, port=None):
        #validate_vlun_params(lunID)

        vlun = "%s,%s" % (volumeName, lunID)

        if hostname:
            vlun += ",%s" % hostname
        else:
            if port:
                vlun += ","

        if port:
            vlun += ",%s:%s:%s" % (port['node'],
                                   port['slot'],
                                   port['cardPort'])

        #print("vlun: ", vlun)
        try:
            #response = self.session_client.rest_client.delete(f"/vluns/{vlun_id}")
            response = self.session_client.rest_client.delete(f"/vluns/{vlun}")
            return response
        except exceptions.HTTPNotFound as e:
            raise
        except HPEStorageException as e:
            raise

    def get_vlun(self, vlun_id):
        validate_vlun_params(vlun_id)
        try:
            response = self.session_client.rest_client.get(f"/vluns/{vlun_id}")
            return response
        except HPEStorageException as e:
            raise

    def getHost(self, name):
        """Get information about a Host.

        :param name: The name of the Host to find
        :type name: str

        :returns: host dict
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_HOST - HOST doesn't exist

        """
        response = self.session_client.rest_client.get(f"/hosts/{name}")
        return response

    def getHostVLUNs(self, hostName):
        """Get all of the VLUNs on a specific Host.

        :param hostName: Host name
        :type hostNane: str

        :returns: list of vluns
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_HOST - HOST doesn't exist

        """
        # calling getHost to see if the host exists and raise not found
        # exception if it's not found.
        self.getHost(hostName)

        vluns = []

        #response, body = self.http.get('/vluns?query=%s' %
        #                               quote(query.encode("utf8")))
        uri = '/vluns?query="hostname EQ %s"' % hostName
        response = self.session_client.rest_client.get(uri)

        for vlun in response.get('members', []):
            vluns.append(vlun)

        return vluns

    def getVLUNs(self):
        """Get all VLUNs.
        In case of 'force detach', hostname is None. Also vlun_id is not known.
        In such scenario, we need list of all VLUNs.

        :returns: Array of VLUNs

        """
        try:
            response = self.session_client.rest_client.get(f"/vluns")
            return response
        except HPEStorageException as e:
            raise

    # PORT Methods
    def _getIscsiVlan(self, nsp):
        """Get iSCSI VLANs for an iSCSI port

        :param nsp: node slot port Eg. '0:2:1'
        :type nsp: str

        :returns: list of iSCSI VLANs

        """
        #response, body = self.http.get('/ports/' + nsp + '/iSCSIVlans/')
        response = self.session_client.rest_client.get(f"/ports/{nsp}/iSCSIVlans/")
        return response

    def getPorts(self):
        """Get the list of ports on the 3PAR.

        :returns: list of Ports

        """
        #response, body = self.http.get('/ports')
        body = self.session_client.rest_client.get(f"/ports")

        # if any of the ports are iSCSI ports and
        # are vlan tagged (as obtained by _getIscsiVlan), then
        # the vlan information is merged with the
        # returned port information.
        for port in body['members']:
            if (port['protocol'] == 2 and
                    'iSCSIPortInfo' in port and
                    port['iSCSIPortInfo']['vlan'] == 1):

                portPos = port['portPos']
                nsp_array = [str(portPos['node']), str(portPos['slot']),
                             str(portPos['cardPort'])]
                nsp = ":".join(nsp_array)
                vlan_body = self._getIscsiVlan(nsp)
                if vlan_body:
                    port['iSCSIVlans'] = vlan_body['iSCSIVlans']

        return body

    def getNvmePorts(self):
        all_ports = self.getPorts()

        target_ports = []
        for port in all_ports['members']:
            if (
                port['mode'] == self.PORT_MODE_TARGET and
                port['linkState'] == self.PORT_STATE_READY
            ):
                port_pos = port['portPos']
                nsp = '%s:%s:%s' % (port_pos['node'], port_pos['slot'],
                                    port_pos['cardPort'])
                port['nsp'] = nsp
                target_ports.append(port)

        nvme_ports = []
        for port in target_ports:
            if port['protocol'] == self.PORT_PROTO_NVME:
                nvme_ports.append(port)

        #logger.debug("nvme_ports: %(ports)s", {'ports': nvme_ports})
        print("nvme_ports: %(ports)s", {'ports': nvme_ports})
        return nvme_ports 

    def get_matched_array_ips_and_ports(self, nvme_ips):
        temp_nvme_ip = {}
        nvme_ip_list = {}
        conf_ips = nvme_ips

        for ip_addr in conf_ips:
            # "ip"(given by user in cinder conf)
            # contains IP Address, NVMe port in <IP>:<PORT> format.
            ip = ip_addr.split(':')
            if len(ip) == 1:
                # "ip" doesn't contain NVMe port, use default NVMe port.
                temp_nvme_ip[ip_addr] = {'ip_port': self.DEFAULT_NVME_PORT}
            elif len(ip) == 2:
                #Valid format <IP>:<PORT>
                temp_nvme_ip[ip[0]] = {'ip_port': ip[1]}
            else:
                #Invalid format such as <IP>:<PORT>:<DATA>
                #logger.warning("Invalid IP address format '%s'", ip_addr)
                print("Invalid IP address format '%s'", ip_addr)

        # get all the valid nvme ports from array
        # when found, add the valid nvme ip and port
        # to the nvme IP dictionary
        nvme_ports = self.getNvmePorts()
        if not len(nvme_ports):
            msg = 'Unable to obtain NVMe ports from storage system.'
            #logger.error(msg)
            #raise exceptions.HTTPNotFound(
            #    {'code': 'NON_EXISTENT_NVME_PORTS',
            #     'desc': msg})
            print("error: ", msg)
            raise HPEStorageException(msg)
        for port in nvme_ports:
            ip = port['nodeWWN']
            if ip in temp_nvme_ip:
                ip_port = temp_nvme_ip[ip]['ip_port']
                nvme_ip_list[ip] = {'ip_port': ip_port,
                                    'nsp': port['nsp']}
                del temp_nvme_ip[ip]

        #logger.debug("After mapping IPs from cinder to storage system:"
        #              "temp_nvme_ip: %(ips)s", {'ips': temp_nvme_ip})
        #logger.debug("After mapping IPs from cinder to storage system:"
        #             "nvme_ip_list: %(ips)s", {'ips': nvme_ip_list})
        print("After mapping IPs from cinder to storage system:"
                      "temp_nvme_ip: %(ips)s", {'ips': temp_nvme_ip})
        print("After mapping IPs from cinder to storage system:"
                     "nvme_ip_list: %(ips)s", {'ips': nvme_ip_list})

        # lets see if there are invalid nvme IPs left in the temp dict
        if len(temp_nvme_ip) > 0:
            #logger.warning("Found invalid nvme IP address(s) in "
            #            "configuration option(s) hpe3par_nvme_ips '%s.'",
            #            (", ".join(temp_nvme_ip)))
            warn_msg = "Found invalid nvme IP address(s) in "
            warn_msg = warn_msg + "configuration option(s) hpe3par_nvme_ips '%s.', ".join(temp_nvme_ip)
            print(warn_msg)

        if not len(nvme_ip_list):
            msg = 'At least one valid nvme IP address must be set.'
            #logger.error(msg)
            #raise exceptions.HTTPNotFound(
            #    {'code': 'NON_EXISTENT_NVME_IP',
            #     'desc': msg})
            print("error: ", msg)
            raise HPEStorageException(msg)

        ret_vals = (nvme_ip_list, nvme_ports)
        return ret_vals

    def getHosts(self):
        """Get information about every Host on the 3Par array.

        :returns: list of Hosts
        """
        response = self.session_client.rest_client.get(f"/hosts")
        return response

    def getHostByNqn(self, nqn):
        """Get information about a Host by its NVMe Qualified Name (NQN).

        :param nqn: The NQN of the Host to find
        :type nqn: str

        :returns: host dict
        :raises: HTTPNotFound
            - NON_EXISTENT_HOST - HOST doesn't exist

        """
        body = self.getHosts()
        if 'members' not in body:
            return None

        for host in body['members']:
            if 'NVMETCPPaths' not in host or not host['NVMETCPPaths']:
                continue
            nvme_paths = host['NVMETCPPaths']
            for path in nvme_paths:
                path_nqn = path.get('NQN')
                if path_nqn == nqn:
                    return host

        # If we reach here, no host with the given NQN was found
        #logger.error("Host with NQN '%s' not found.", nqn)
        msg = "Host with NQN '%s' not found." % nqn
        #raise exceptions.HTTPNotFound(error={'desc': msg})
        print("Error: Host with NQN '%s' not found.", nqn)
        msg = "Host with NQN '%s' not found." % nqn
        #raise Exception(msg)
        return None

    def getNqn(self, portPos=None):
        # in dev and QA array, all ports have same nqn below:
        # 'nqn.2014-08.org.nvmexpress.discovery'
        return self.DEFAULT_PORT_NQN

    def build_portPos(self, nsp):
        arr = nsp.split(":")
        portPos = {}
        portPos['node'] = int(arr[0])
        portPos['slot'] = int(arr[1])
        portPos['cardPort'] = int(arr[2])
        return portPos

    def find_existing_vluns(self, vol_name_3par, host):
        existing_vluns = []
        try:
            host_vluns = self.getHostVLUNs(host['name'])
            for vlun in host_vluns:
                if vlun['volumeName'] == vol_name_3par:
                    existing_vluns.append(vlun)
        #except exceptions.HTTPNotFound:
        except Exception as ex:
            # ignore, no existing VLUNs were found
            print("No existing VLUNs were found for host/volume "
                         "combination: %(host)s, %(vol)s",
                         {'host': host['name'],
                          'vol': vol_name_3par})
        return existing_vluns

    def getVLUN(self, volumeName, allVluns=False):
        """Get information about a VLUN.

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            -  NON_EXISTENT_VLUN - VLUN doesn't exist

        """
        #query = '"volumeName EQ %s"' % volumeName
        #response, body = self.http.get('/vluns?query=%s' %
        #                               quote(query.encode("utf8")))
        uri = '/vluns?query="volumeName EQ %s"' % volumeName
        response = self.session_client.rest_client.get(uri)

        if allVluns:
            # Return all the VLUNs found for the volume.
            vluns = response.get('members', [])
            return vluns
        else:
            # Return the first VLUN found for the volume.
            for vlun in response.get('members', []):
                return vlun

    def getNextLunId(self, hostname, host_type='nvme'):
        # lun id can be 0 through 16383 (1 to 256 for NVMe hosts)
        LIMIT = 16383
        if host_type=='nvme':
            LIMIT = 256

        lun_id_max = 0
        try:
            host_vluns = self.getHostVLUNs(hostname)
            for vlun in host_vluns:
                lun_id_x = vlun['lun']
                if lun_id_x > lun_id_max:
                    lun_id_max = lun_id_x

        #except exceptions.HTTPNotFound:
        except HPEStorageException as e:
            # ignore, no existing VLUNs were found
            pass

        lun_id_next = lun_id_max + 1
        if lun_id_next > LIMIT:
            msg = "Lun id exceeded limit '%d'" % LIMIT
            #raise exceptions.HTTPNotFound(error={'desc': msg})
            raise Exception(msg)

        return lun_id_next

    def remove_vlun_nvme(self, vol_name_3par, hostname, host_nqn):
        vlunsData = self.getVLUN(vol_name_3par, True)
        print("vlunsData: ", vlunsData)
        if vlunsData == []:
            #logger.error("No VLUN found for volume %(name)s on host %(host)s",
            #             {'name': vol_name_3par, 'host': hostname})
            print("Error: No VLUN found for volume %(name)s on host %(host)s",
                         {'name': vol_name_3par, 'host': hostname})
            return

        # When deleteing VLUNs, you simply need to remove the template VLUN
        # and any active VLUNs will be automatically removed.  The template
        # VLUN are marked as active: False
        vluns = []
        for vlun in vlunsData:
            if vol_name_3par in vlun['volumeName']:
                # template VLUNs are 'active' = False
                if not vlun['active']:
                    vluns.append(vlun)

        print("vluns: ", vluns)
        if not vluns:
            #logger.warning("3PAR vlun for volume %(name)s not found on host "
            #               "%(host)s", {'name': vol_name_3par, 'host': hostname})
            print("Warning: 3PAR vlun for volume %(name)s not found on host "
                        "%(host)s", {'name': vol_name_3par, 'host': hostname})
            return

        for vlun in vluns:
            print("  -- vlun: ", vlun)
            # In a normal detach a hostname is supplied and we only remove
            # that host's VLUN. In a force-detach there is no connector, so
            # hostname is None; fall back to the hostname on the VLUN record
            # itself (mirrors remove_vlun() for FC/iSCSI) so the template is
            # still removed and the active VLUN is cascaded away.
            vlun_hostname = vlun.get('hostname')
            if hostname is not None and vlun_hostname != hostname:
                #logger.debug("Skipping vlun: %(lun)s -"
                print("Skipping vlun: %(lun)s -"
                             " belongs to different host: %(vlun_host)s",
                             {'lun': vlun['lun'],
                              'vlun_host': vlun_hostname or 'Unknown'})
                continue
            #logger.debug("deleting vlun: %(lun)s", {'lun': vlun})
            print("deleting vlun")
            self.delete_vlun(vol_name_3par, vlun['lun'], vlun_hostname)


