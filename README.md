# Small Office Enterprise Network Simulation (GPE)

A 4-department enterprise network architecture designed and simulated in **Cisco Packet Tracer**. The network implements hierarchical switching, VLAN segmentation, Router-on-a-Stick (802.1Q) inter-VLAN routing, and centralized network infrastructure services (DHCP, DNS, and HTTP).

---

## Network Architecture Blueprint

![Network Architecture Diagram](network_diagram.svg)

---

## Cisco Packet Tracer Simulation View

![Small Office Network Topology](Screenshot.png)

---

## Logical Wiring & Port Topology

```mermaid
flowchart TD
    classDef router fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px;
    classDef coreSwitch fill:#e0e7ff,stroke:#4338ca,stroke-width:2px;
    classDef deptSwitch fill:#ede9fe,stroke:#6d28d9,stroke-width:2px;
    classDef host fill:#f0fdf4,stroke:#15803d,stroke-width:1.5px;
    classDef server fill:#fff7ed,stroke:#c2410c,stroke-width:2px;

    ROUTER["<b>Main Router</b><br/>Cisco 2911<br/>Router-on-a-Stick (802.1Q)<br/>Gateways: 192.168.x.1"]:::router
    CORE["<b>Core Switch</b><br/>Cisco 2960-24TT<br/>Trunk Uplinks: VLANs 10, 20, 30, 40"]:::coreSwitch

    ROUTER ---|"Gig0/0 ═══ Gig0/1<br/>(802.1Q Trunk)"| CORE

    subgraph MGT_BOX ["Management Room (VLAN 10 | 192.168.10.0/24)"]
        SW_MGT["<b>Management Switch</b><br/>Cisco 2960-24TT"]:::deptSwitch
        PC_M1["<b>Manager Computer</b><br/>IP: Dynamic (DHCP)<br/>Gateway: 192.168.10.1"]:::host
        PC_M2["<b>Employee Computer 1</b><br/>IP: Dynamic (DHCP)<br/>Gateway: 192.168.10.1"]:::host
        SW_MGT ---|"Fa0/2 ── Fa0"| PC_M1
        SW_MGT ---|"Fa0/3 ── Fa0"| PC_M2
    end

    subgraph HR_BOX ["HR Room (VLAN 20 | 192.168.20.0/24)"]
        SW_HR["<b>HR Switch</b><br/>Cisco 2960-24TT"]:::deptSwitch
        PC_H1["<b>HR Manager Computer</b><br/>IP: Dynamic (DHCP)<br/>Gateway: 192.168.20.1"]:::host
        PC_H2["<b>Employee Computer 2</b><br/>IP: Dynamic (DHCP)<br/>Gateway: 192.168.20.1"]:::host
        SW_HR ---|"Fa0/2 ── Fa0"| PC_H1
        SW_HR ---|"Fa0/3 ── Fa0"| PC_H2
    end

    subgraph IT_BOX ["IT Room (VLAN 30 | 192.168.30.0/24)"]
        SW_IT["<b>IT Switch</b><br/>Cisco 2960-24TT"]:::deptSwitch
        PC_I1["<b>IT Admin Computer</b><br/>IP: Dynamic (DHCP)<br/>Gateway: 192.168.30.1"]:::host
        PC_I2["<b>Employee Computer 3</b><br/>IP: Dynamic (DHCP)<br/>Gateway: 192.168.30.1"]:::host
        SW_IT ---|"Fa0/2 ── Fa0"| PC_I1
        SW_IT ---|"Fa0/3 ── Fa0"| PC_I2
    end

    subgraph SRV_BOX ["Server Room (VLAN 40 | 192.168.40.0/24)"]
        SRV["<b>Main Server</b><br/>Server-PT<br/>IP: 192.168.40.10 /24<br/>Gateway: 192.168.40.1<br/>Services: DHCP + DNS + HTTP<br/>Web: http://office.local"]:::server
    end

    CORE ---|"Fa0/1 ═══ Fa0/1<br/>(802.1Q Trunk)"| SW_MGT
    CORE ---|"Fa0/2 ═══ Fa0/1<br/>(802.1Q Trunk)"| SW_HR
    CORE ---|"Fa0/3 ═══ Fa0/1<br/>(802.1Q Trunk)"| SW_IT
    CORE ---|"Fa0/4 ─── Fa0<br/>(VLAN 40 Access)"| SRV
```

---

## Detailed Physical & Logical Port Wiring Table

| Uplink Source Device  | Source Port          | Destination Device      | Destination Port     | Link Mode |     Encapsulation / VLAN      |
| :-------------------- | :------------------- | :---------------------- | :------------------- | :-------: | :---------------------------: |
| **Main Router**       | `GigabitEthernet0/0` | **Core Switch**         | `GigabitEthernet0/1` |   Trunk   | 802.1Q (VLANs 10, 20, 30, 40) |
| **Core Switch**       | `FastEthernet0/1`    | **Management Switch**   | `FastEthernet0/1`    |   Trunk   | 802.1Q (VLANs 10, 20, 30, 40) |
| **Core Switch**       | `FastEthernet0/2`    | **HR Switch**           | `FastEthernet0/1`    |   Trunk   | 802.1Q (VLANs 10, 20, 30, 40) |
| **Core Switch**       | `FastEthernet0/3`    | **IT Switch**           | `FastEthernet0/1`    |   Trunk   | 802.1Q (VLANs 10, 20, 30, 40) |
| **Core Switch**       | `FastEthernet0/4`    | **Main Server**         | `FastEthernet0`      |  Access   |     VLAN 40 (Server Room)     |
| **Management Switch** | `FastEthernet0/2`    | **Manager Computer**    | `FastEthernet0`      |  Access   |     VLAN 10 (Management)      |
| **Management Switch** | `FastEthernet0/3`    | **Employee Computer 1** | `FastEthernet0`      |  Access   |     VLAN 10 (Management)      |
| **HR Switch**         | `FastEthernet0/2`    | **HR Manager Computer** | `FastEthernet0`      |  Access   |         VLAN 20 (HR)          |
| **HR Switch**         | `FastEthernet0/3`    | **Employee Computer 2** | `FastEthernet0`      |  Access   |         VLAN 20 (HR)          |
| **IT Switch**         | `FastEthernet0/2`    | **IT Admin Computer**   | `FastEthernet0`      |  Access   |         VLAN 30 (IT)          |
| **IT Switch**         | `FastEthernet0/3`    | **Employee Computer 3** | `FastEthernet0`      |  Access   |         VLAN 30 (IT)          |

---

## IP Addressing & VLAN Allocation

| Department / Zone   |  VLAN ID  |      Subnet       |   Gateway IP   |   DNS Server    |      IP Assignment       |
| :------------------ | :-------: | :---------------: | :------------: | :-------------: | :----------------------: |
| **Management**      | `VLAN 10` | `192.168.10.0/24` | `192.168.10.1` | `192.168.40.10` |      Dynamic (DHCP)      |
| **Human Resources** | `VLAN 20` | `192.168.20.0/24` | `192.168.20.1` | `192.168.40.10` |      Dynamic (DHCP)      |
| **IT Department**   | `VLAN 30` | `192.168.30.0/24` | `192.168.30.1` | `192.168.40.10` |      Dynamic (DHCP)      |
| **Server Room**     | `VLAN 40` | `192.168.40.0/24` | `192.168.40.1` | `192.168.40.10` | Static (`192.168.40.10`) |

---

## Device Role & Naming Directory

| Display Name            | Device Hardware | IOS Hostname        | Department / Zone | Role & Function                                 |
| :---------------------- | :-------------- | :------------------ | :---------------- | :---------------------------------------------- |
| **Main Router**         | Cisco 2911      | `Main-Router`       | Central Routing   | 802.1Q Inter-VLAN Gateway & DHCP Relay          |
| **Core Switch**         | Cisco 2960-24TT | `Core-Switch`       | Core Distribution | 802.1Q Trunk Aggregator for all VLANs           |
| **Management Switch**   | Cisco 2960-24TT | `Management-Switch` | Management Room   | Access switch for VLAN 10                       |
| **Manager Computer**    | PC-PT           | —                   | Management Room   | Management department lead workstation          |
| **Employee Computer 1** | PC-PT           | —                   | Management Room   | Management department staff workstation         |
| **HR Switch**           | Cisco 2960-24TT | `HR-Switch`         | HR Room           | Access switch for VLAN 20                       |
| **HR Manager Computer** | PC-PT           | —                   | HR Room           | Human Resources manager workstation             |
| **Employee Computer 2** | PC-PT           | —                   | HR Room           | Human Resources staff workstation               |
| **IT Switch**           | Cisco 2960-24TT | `IT-Switch`         | IT Room           | Access switch for VLAN 30                       |
| **IT Admin Computer**   | PC-PT           | —                   | IT Room           | IT Network & Systems Administrator PC           |
| **Employee Computer 3** | PC-PT           | —                   | IT Room           | IT Technical Support workstation                |
| **Main Server**         | Server-PT       | —                   | Server Room       | Hosts DHCP Pools, DNS, and Corporate Web Server |

---

## Core Network Services

### 1. Inter-VLAN Routing (Router-on-a-Stick)

Routing between departmental subnets is performed via subinterfaces on **Main Router** (`GigabitEthernet0/0`):

- `g0/0.10`: Encapsulation `dot1Q 10`, IP `192.168.10.1 255.255.255.0`
- `g0/0.20`: Encapsulation `dot1Q 20`, IP `192.168.20.1 255.255.255.0`
- `g0/0.30`: Encapsulation `dot1Q 30`, IP `192.168.30.1 255.255.255.0`
- `g0/0.40`: Encapsulation `dot1Q 40`, IP `192.168.40.1 255.255.255.0`

### 2. DHCP Relay (`ip helper-address`)

Since the DHCP server resides on VLAN 40 (`192.168.40.10`), each router subinterface is configured with:

```ios
ip helper-address 192.168.40.10
```

This forwards client broadcast DHCP Discover packets as unicast packets to the central server.

### 3. DNS & Intranet Web Service

- **DNS Server**: Mapped domain `office.local` $\rightarrow$ `192.168.40.10`.
- **HTTP Web Server**: Active on port 80 serving the corporate intranet homepage. Any PC can test connectivity by browsing to `http://office.local` or `http://192.168.40.10`.

---

## Workspace Files

- [`network_diagram.svg`](network_diagram.svg) — Vector architecture blueprint with port-level wiring and departmental zoning.
- [`Small_Office_4_DepartmentSs.pkt`](Small_Office_4_DepartmentSs.pkt) — Active Cisco Packet Tracer project file with simplified names and synchronized IOS configurations.
- [`Screenshot.png`](Screenshot.png) — Visual snapshot of the network layout and simulation canvas.
- [`son.png`](son.png) — Visual reference template for simplified device naming and layout.
