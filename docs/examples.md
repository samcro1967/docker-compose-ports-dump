Examples of port.mapping configuration in a docker-compose.yml file

./dcpd_main.py -s

1. Service attached to VPN container:
services:
  my_service1:
    environment:
      - port.mapping=51820
      # Additional environment variables...
    network_mode: service:your_vpn_container_name

In example 1:
The 'my_service1' is attached to the VPN container 'your_vpn_container_name'.
The 'port.mapping' environment variable is set to '51820', which represents the external port that should be mapped to the service
 'your_vpn_container_name'.
The 'port.mapping' can be anywhere in the environment block. It does not need to be first or last.

2. Another service attached to VPN container:
services:
  my_service2:
    environment:
      - port.mapping=1194
      - port.mapping1=1195
      - port.mapping2=1196
      # Additional environment variables...
    network_mode: service:your_vpn_container_name

In example 2:
'my_service2' is another service that is attached to the VPN container 'your_vpn_container_name'.
It has three 'port.mappings' environment variables set to '1194, 1195, & 1196', representing the external ports mapped to the service 'your_vpn_container_name'.
The 'port.mappings' can be anywhere in the environment block. It does not need to be first or last.

3. Another service not attached to VPN container:
services:
  my_service3:
    ports:
     - 8923:8080

In example 3:
'my_service3' is another service that is not attached to the VPN container 'your_vpn_container_name'.
It has one external port, '8923', mapped to the internal port '8080'.

4. Your VPN Container:
services:
  vpn_container_name:
    ports:
      - 1194:1194
      - 1195:1195
      - 1196:1196
      - 51820:51820

In example 4:
'vpn_container_name' is the name of your VPN container.
It has four ports mapped, '1194, 1195, 1196, & 51820' for the 2 containers that are attaching to its network, 'my_service1' and 'my_service2'.