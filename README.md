# onapp-template-script

OOP implementation of OnApp OVF

In order to create the template, first install OnApp along with the open-vm-tools, perl and net-tools.
In vCenter click on the VM and select "Configure" (right side pane, next to Summary and Monitor), select vApp Options under settings menu.
Enable the vApp options and provide the Details.
For IP allocation select OVF Environment.
For OVF settings OVF environment transport should be set to VMware Tools and Installation boot should be disabled.
Under Properties add the following Keys (without ''):

'onapp_dns'
'onapp_fqdn'
'onapp_gw'
'onapp_ipaddr'
'onapp_netmask'

Also create a rabbitmq-env.conf in /etc/rabbitmq and copy rabbitmq-env.conf file in this repository over there.

The following steps will set up the script to run on boot and configure based on above properties:

mkdir -r /etc/rabbitmq (move the rabbitmq-env file to this location for static rabbitmq hostname)

yum install python3

pip3 install --upgrade pip

pip3 install requests

mkdir -p /root/scripts/onapp-firstboot

cd /root/scripts/onapp-firstboot

git clone https://github.com/umaars/onapp-template-script.git .

cp onapp-boot.service /etc/systemd/system/onapp-boot.service

chmod 644 /etc/systemd/system/onapp-boot.service

systemctl daemon-reload

systemctl enable onapp-boot.service
