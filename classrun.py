from xml.dom import minidom
from pathlib import Path
import subprocess
import sys
import requests
import fileinput
import os
import time


def xmlparser():
    '''
    Parses a vmware tools XML file and returns all properties in a dictionary
    '''
    with open('sample.xml', 'w') as f:
        p1 = subprocess.run(
            'vmtoolsd --cmd "info-get guestinfo.ovfEnv" >> sample.xml', stdout=f, shell=True)
        f.close()
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
        #self.onapp_license = kwargs['onapp_license']
        self.onapp_netmask = kwargs['onapp_netmask']

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
        hostname_command = f"hostnamectl set-hostname {self.onapp_fqdn}"
        x = subprocess.Popen(hostname_command.split(' '))
        x.wait()
        y = subprocess.Popen('hostnamectl')
        return y

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

    def updateSNMP(self):
        cmd = f"/onapp/onapp-cp-install/onapp-cp-install.sh -a --quick -i {self.onapp_ipaddr}"
        x = subprocess.Popen(cmd.split(' '))
        x.wait()

    # Not needed as we are using rabbitmq-env.conf file to set a static hostname for rabbitmq install.
    #  @staticmethod
    # def reinstall_rabbitmq():
    #     rabbitmq_cmd = "/onapp/onapp-rabbitmq/onapp-cp-rabbitmq.sh"
    #     x = subprocess.Popen(rabbitmq_cmd)
    #     x.wait()
    #     return "finished"

    @staticmethod
    def change_install_uuid():
        uuid_command = '''su onapp -c "cd /onapp/interface && rails runner -e production 'ApplicationState.regenerate_install_uuid'"'''
        os.system('uuid_command')
        print("UUID changed")

    def __str__(self):
        data = f"'onapp_dns': {self.onapp_dns}, 'onapp_fqdn': {self.onapp_fqdn}, 'onapp_gw': {self.onapp_gw}, 'onapp_ipaddr': {self.onapp_ipaddr}, 'onapp_license': {self.onapp_license}, onapp_netmask: {self.onapp_netmask},'onapp_license': {self.onapp_license},"
        return data


p = OvfProperties(**xmlparser())

if os.path.isfile('/root/first-run'):
    # if os.path.isfile('/root/second-run'):
    print("skipping first time configuration")
    # else:
    #     p.reinstall_rabbitmq()
    #     time.sleep(2)
    #     Path('/root/second-run').touch()
    #     time.sleep(2)
    #     os.system('shutdown -r now')

else:
    print(p.setNetwork("/etc/sysconfig/network-scripts/ifcfg-ens160"))
    p.setHostname()
    Path('/root/first-run').touch()
    # p.setLicense()
    time.sleep(5)
    p.change_install_uuid()
    p.updateSNMP()
    os.system('shutdown -r now')
