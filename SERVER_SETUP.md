# SERVER0 configuration in Packet Tracer

The Server-PT must be configured through its graphical interface; the Cisco IOS configuration files do not configure Server-PT services.

## Static address

In **Desktop > IP Configuration**, set IPv4 address `192.168.40.10`, subnet mask `255.255.255.0`, default gateway `192.168.40.1`, and DNS server `192.168.40.10`.

## DHCP

In **Services > DHCP**, select the FastEthernet interface, turn the service **On**, and create these three pools. Click **Add** or **Save** for each pool. If a default `serverPool` already exists, remove or disable it to avoid handing out an unintended subnet.

| Pool name | Default gateway | DNS server | Start IP | Subnet mask | Maximum users |
| --- | --- | --- | --- | --- | ---: |
| ACCOUNTS | 192.168.10.1 | 192.168.40.10 | 192.168.10.100 | 255.255.255.0 | 50 |
| HR | 192.168.20.1 | 192.168.40.10 | 192.168.20.100 | 255.255.255.0 | 50 |
| IT | 192.168.30.1 | 192.168.40.10 | 192.168.30.100 | 255.255.255.0 | 50 |

The router's `ip helper-address` relays DHCP requests from the three client VLANs to this server. The server uses a fixed address in VLAN 40 and does not need a VLAN 40 DHCP pool.

## DNS

In **Services > DNS**, turn the service **On**. Add an **A Record** with name `office.local` and address `192.168.40.10`. Save it. Packet Tracer's browser may accept either `http://office.local` or `office.local`.

## HTTP

In **Services > HTTP**, turn **HTTP On**. Edit `index.html`: replace its contents with the complete contents of `web/index.html`, then click **Save**. HTTPS is optional and not part of this base.
