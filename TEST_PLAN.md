# Verification checklist

Run these checks after the build is saved. The first DHCP attempt may need a few seconds while the trunks and spanning tree converge.

| Test | Where / command | Expected result |
| --- | --- | --- |
| VLANs | Each switch: `show vlan brief` | VLANs 10, 20, 30, 40 exist; PC access ports are in the correct VLAN |
| Trunks | SW-CORE: `show interfaces trunk` | Gi0/1 and Fa0/1-3 trunk; VLANs 10,20,30,40 allowed |
| Router gateways | R1-OMS: `show ip interface brief` | Gi0/0.10/.20/.30/.40 are up/up after links converge |
| DHCP | Each PC: Desktop > IP Configuration | Accounts 192.168.10.100-149, HR 20.100-149, IT 30.100-149; correct gateway and DNS |
| DHCP relay | R1-OMS: `show running-config` | `ip helper-address 192.168.40.10` on subinterfaces 10, 20, 30 |
| Server connectivity | ACC-PC1: `ping 192.168.40.10` | Replies after ARP warm-up |
| Allowed interdepartment | ACC-PC1: ping the DHCP address shown on HR-PC1 | Replies |
| Allowed IT to HR | IT-PC1: ping the DHCP address shown on HR-PC1 | Replies |
| Blocked IT to Accounts | IT-PC1: ping the DHCP address shown on ACC-PC1 | Fails; router ACL deny counter increases |
| DNS | Any PC: `ping office.local` | Name resolves to 192.168.40.10 and replies |
| Website | Any PC: Desktop > Web Browser > `http://office.local` | Office Management System landing page appears |
| ACL counter | R1-OMS: `show access-lists IT_TO_ACCOUNTS` | Deny line has matches after blocked ping |

`ping` can lose the first packet while ARP resolves. Repeat once before diagnosing. A test against `192.168.10.1` from IT is not a valid blocked test: the ACL specifically blocks the Accounts *subnet*, including its gateway in principle, but Packet Tracer router behavior can vary for packets destined to its own interface. Test against ACC-PC1.

If DHCP fails, check the Server-PT service is On, its three pools are saved, the server static gateway is correct, core Fa0/4 is VLAN 40, trunks allow VLANs 10-40, and router subinterfaces are up. If DNS fails but IP ping works, check the DNS service, record, and PC lease DNS field.
