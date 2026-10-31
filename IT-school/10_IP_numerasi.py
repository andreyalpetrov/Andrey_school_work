import ipaddress
net = ipaddress.ip_network('192.121.68.6/255.255.224.0', 0)
print(net[-2])
