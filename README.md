# Office Management System Using Cisco Packet Tracer

This is a build-ready base for a Computer Networks group project. It follows the supplied two-page design: Accounts, HR, IT, and Server VLANs; router-on-a-stick routing; central DHCP, DNS, and HTTP; and an ACL that prevents IT from reaching Accounts. The source example in `reference/` is a different topology and is supplied only for comparison.

**Status:** Configuration files and construction instructions are complete. No new `.pkt` file is included, because Cisco Packet Tracer was unavailable in the creation environment. A team member must assemble the topology in Packet Tracer and save it as `Office_Management_System_Base.pkt`. Do not submit `reference/SmallOfficeNetwork_Original.pkt` as the new project.

## Topology and devices

Use one 2911 router, four 2960-24TT switches (one core plus three department switches), one Server-PT, and six PC-PT devices. Use Copper Straight-Through cables or Packet Tracer's automatic connection tool. Arrange the router above the core, three department switches below it, two PCs under each department, and the server alongside the core. Name devices exactly as shown below so configuration files match.

| Device A / interface | Device B / interface | Purpose |
| --- | --- | --- |
| R1-OMS Gi0/0 | SW-CORE Gi0/1 | VLAN trunk |
| SW-CORE Fa0/1 | SW-ACCOUNTS Fa0/1 | VLAN trunk |
| SW-CORE Fa0/2 | SW-HR Fa0/1 | VLAN trunk |
| SW-CORE Fa0/3 | SW-IT Fa0/1 | VLAN trunk |
| SW-CORE Fa0/4 | SERVER0 Fa0 | Server VLAN 40 |
| SW-ACCOUNTS Fa0/2, Fa0/3 | ACC-PC1, ACC-PC2 Fa0 | Accounts VLAN 10 |
| SW-HR Fa0/2, Fa0/3 | HR-PC1, HR-PC2 Fa0 | HR VLAN 20 |
| SW-IT Fa0/2, Fa0/3 | IT-PC1, IT-PC2 Fa0 | IT VLAN 30 |

## Address plan

| Role | VLAN | Network | Gateway | DHCP client range |
| --- | ---: | --- | --- | --- |
| Accounts | 10 | 192.168.10.0/24 | 192.168.10.1 | 192.168.10.100-149 |
| HR | 20 | 192.168.20.0/24 | 192.168.20.1 | 192.168.20.100-149 |
| IT | 30 | 192.168.30.0/24 | 192.168.30.1 | 192.168.30.100-149 |
| Server | 40 | 192.168.40.0/24 | 192.168.40.1 | Static server: 192.168.40.10 |

All masks are `255.255.255.0`. DNS is `192.168.40.10`. The internal site name is `office.local`.

## Build sequence

1. Place and name all devices, then cable the exact ports in the topology table. The 2960-24TT has Gigabit ports and FastEthernet ports; use the specified ones.
2. On each switch, open **CLI**, answer `no` to the initial configuration dialog if shown, press Return, and paste the matching file from `configs/`. Let any initial spanning-tree delay settle. If the CLI rejects `write memory` in your version, use `copy running-config startup-config`.
3. On the router, open **CLI** and paste `configs/R1-OMS.txt`. If a different router model is used, change *every* `GigabitEthernet0/0` interface name in that file to the router's actual connected port before pasting. The 2911 model is the intended choice.
4. Configure SERVER0 in **Desktop > IP Configuration**: static IP `192.168.40.10`, mask `255.255.255.0`, gateway `192.168.40.1`, DNS `192.168.40.10`.
5. Configure SERVER0 services exactly as described in `SERVER_SETUP.md`. Paste `web/index.html` into the HTTP service's `index.html` editor.
6. On each PC, open **Desktop > IP Configuration > DHCP**. If a PC has an old address, toggle Static then DHCP. Wait for a valid address from its department range.
7. Run the checks in `TEST_PLAN.md`. Finally save the Packet Tracer file through **File > Save As** using `Office_Management_System_Base.pkt`.

## How teammates can extend it

Reserve switch access ports Fa0/4-Fa0/24 for new endpoints. Additional Accounts PCs should go on SW-ACCOUNTS in VLAN 10, and similarly for HR and IT. The DHCP pools currently have 50 addresses each; increase the maximum if needed. New services can use free static addresses in VLAN 40 outside the DHCP ranges, for example `192.168.40.20`. Document any new ACLs because the current rule intentionally blocks only IT to Accounts.

## Scope of the base

The web page is a demonstrable intranet landing page. Packet Tracer's built-in HTTP server displays static HTML; it is not an employee database or a production office application. Accounts and HR can communicate with each other and the server. IT can communicate with HR and the server, but cannot communicate with Accounts. The router interfaces remain reachable for troubleshooting.

## Reference and licensing

The original `SmallOfficeNetwork_Original.pkt`, image, and MIT license are from the supplied `small-office-network-main` folder. This base's design, configuration files, and documentation are newly written for the supplied office management design.
