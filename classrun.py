from xml.dom import minidom
import subprocess

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
    
    def setNetwork(self):
        network_props = {
            'BOOTPROTO': "BOOTPROTO=static",
            "NETMASK=": f"NETMASK={self.onapp_netmask}",
            "IPADDR=": f"IPADDR={self.onapp_ipaddr}",
            'GATEWAY=': f"GATEWAY={self.onapp_gw}",
            'DNS1=': f'DNS1={self.onapp_dns}',
        }
        return network_props

    def setHostname(self):
        # hostname_command = f"hostnamectl set-hostname {self.onapp_fqdn}"
        hostname_command = f"hostnamectl set-hostname {self.onapp_fqdn}"
        x = subprocess.run(hostname_command.split(' '))
        x.check_output()
        return hostname_command
        
    def __str__(self):
        data = f"'onapp_dns': {self.onapp_dns}, 'onapp_fqdn': {self.onapp_fqdn}, 'onapp_gw': {self.onapp_gw}, 'onapp_ipaddr': {self.onapp_ipaddr}, 'onapp_license': {self.onapp_license}, onapp_netmask: {self.onapp_netmask},'onapp_license': {self.onapp_license},"
        return data


p = OvfProperties(**xmlparser())
print(p)
print(p.setNetwork())
print(p.setHostname())
