import ipaddress
net = ipaddress.ip_network('192121/255.255.224.0', 0)
print(net[-2])
