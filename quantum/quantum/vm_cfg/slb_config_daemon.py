# SLB VM Configuration Daemon
import sys
import time
import os


class SLBVMConfigurationDaemon(object):
    """
    SLBVMConfigurationDaemon class implements the SLB VM configuration routines 
    required for the updates to the configuration of the SLB.
    Here, HA-Proxy
    """
    def __init__(self):
        """
        Initializing the data required
        """
        self.response = ''
        self.tmp_path ="/tmp/haproxy.cfg"
        self.haproxy_cfg_path ="/etc/haproxy/haproxy.cfg"
        
    def _handle_loadbalancer_config(self,request_dict):
        """
        Handles update of HA-Proxy Configuration
        and Resuests from Compute node.
        """
        self.client_api = 'dummy.api'
        request_dict['client_api'] = self.client_api
        if request_dict['header'] == 'request':
            json_data = self._prepare_response(request_dict)
        elif request_dict['header'] == 'data':
            # TODO (Trinath) for now dont send response for DATA header
            self._handle_request_data(request_dict)
        return json_data

    def _handle_request_data(self,request_dict):
        """
        Handles 'data' header and prepares the 
        response json.
        """
        self._write_file(self.tmp_path,request_dict['data'])
        check_cfg = os.popen("haproxy -c -f {0}".self.tmp_path)
        print check_cfg
        # TODO (trinath) Check the return status of the above 
        # haproxy command, and work the next operation
        self._write_file(self.haproxy_cfg_path,request_dict['data'])
        json_data = self._prepare_response(request_dict)
        os.system("service haproxy restart")
        return json_data


    def _prepare_response(self,request):
        """
        Prepare the JSON formatted Response data.
        """
        data = {"header":"response",
                "config_handle_id":request['config_handle_id'],
                "slug":request['slug'],
                "client_api":request['client_api'],
                "version":"0.0",
               }
        return data

    def _write_file(self,path,data):
        """
        writes the file in the specified location
        """
        with open(path,"w") as fd:
            fd.write(data)
            fd.close()


    def daemon_loop(self):
        """
        Loop to find the incoming config change requests
        and update and restart the SLB.
        """
        fd = open("/dev/virtio-ports/ns_port",'a+')
        fd.write("{'method':'hello','msg':'Config Daemon is UP'}")
        while True:
            request_dict = fd.read(65535)
            if self.request_dict['slug'] == 'loadbalancer':
                self.response = self._handle_loadbalancer_config(self.request_dict)
            if self.response:
                fd.write(self.response)

            
def main():
    """
    Start the Daemon Loop with required data
    """
    VmConf = SLBVMConfigurationDaemon()
    VmConf.deamon_loop()
    sys.exit(0)
    pass


if __name__ == "__main__":
    main()



    


