from xml.dom import minidom
import subprocess
import sys
import requests
import fileinput


def xmlparser():
    '''
    Parses a vmware tools XML file and returns all properties in a dictionary
    '''
    # with open('sample.xml', 'w') as f:
    #     p1 = subprocess.run(
    #         'vmtoolsd --cmd "info-get guestinfo.ovfEnv" >> sample.xml', stdout=f, shell=True)
    #     f.close()
    PROPERTIES = {}
    p = minidom.parse('sample.xml')
    item_list = p.getElementsByTagName('Property')
    for i in item_list:
        key = i.attributes['oe:key'].value
        value = i.attributes['oe:value'].value
        PROPERTIES[key] = value
    return PROPERTIES


class OvfProperties:
    def __init__(self, **kwargs):
        self.onapp_dns = kwargs['onapp_dns']
        self.onapp_fqdn = kwargs['onapp_fqdn']
        self.onapp_gw = kwargs['onapp_gw']
        self.onapp_ipaddr = kwargs['onapp_ipaddr']
        self.onapp_license = kwargs['onapp_license']
        self.onapp_netmask = kwargs['onapp_netmask']
        self.onapp_license = kwargs['onapp_license']

    def setNetwork(self, file_to_change):
        network_props = {
            'BOOTPROTO': "BOOTPROTO=static",
            'NETMASK=': f"NETMASK={self.onapp_netmask}",
            'IPADDR=': f"IPADDR={self.onapp_ipaddr}",
            'GATEWAY=': f"GATEWAY={self.onapp_gw}",
            'DNS1=': f'DNS1={self.onapp_dns}',
        }
        mylist = list(network_props.keys())
        for line in fileinput.input(files=(file_to_change), inplace=1):
            for each in mylist:
                if each in line:
                    line = f"{network_props[each]}\n"
                else:
                    line = line
            print(line, end='')

        return network_props

    def setHostname(self):
        # hostname_command = f"hostnamectl set-hostname {self.onapp_fqdn}"
        hostname_command = f"sleep 5"
        x = subprocess.Popen(hostname_command.split(' '))
        print("waiting 5 seconds")
        x.wait()
        print("wait over")

        return "hello"

    def setLicense(self):
        r = requests.Session()
        r.headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }
        r.auth = 'admin', 'changeme'
        url = 'http://localhost/settings.json'
        license_key = self.onapp_license
        payload = {"configuration": {
            "isolated_license": "true", "license_key": license_key}}
        data = r.put(url, json=payload)
        return data.headers

    @staticmethod
    def reinstall_rabbitmq():
        rabbitmq_cmd = "/onapp/onapp-rabbitmq/onapp-cp-rabbitmq.sh"
        x = subprocess.Popen(rabbitmq_cmd)
        x.wait()
        return "finished"

    def __str__(self):
        data = f"'onapp_dns': {self.onapp_dns}, 'onapp_fqdn': {self.onapp_fqdn}, 'onapp_gw': {self.onapp_gw}, 'onapp_ipaddr': {self.onapp_ipaddr}, 'onapp_license': {self.onapp_license}, onapp_netmask: {self.onapp_netmask},'onapp_license': {self.onapp_license},"
        return data


p = OvfProperties(**xmlparser())
print(p)
print(p.setNetwork("ifcfg-ens192"))
# print(p.setHostname())
# print(p.reinstall_rabbitmq())
