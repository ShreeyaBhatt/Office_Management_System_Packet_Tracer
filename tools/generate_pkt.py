"""Generate Office_Management_System_Base.pkt directly, without opening Packet Tracer.

Requires: pip install packet-tracer-pkt-format
Reads configs/ and web/index.html, so re-run this after changing either.
"""
import re
import uuid
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from make_builder_script import IOS_DEVICES, ios_commands
from pkt_core.builder.lab import Lab, load_templates
from pkt_core.resources import load_network_seed

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "Office_Management_System_Base.pkt"

MASK = "255.255.255.0"
SERVER_IP = "192.168.40.10"
SERVER_GATEWAY = "192.168.40.1"
VLANS = {10: "ACCOUNTS", 20: "HR", 30: "IT", 40: "SERVER"}

DEVICES = [
    ("R1-OMS", "2911", 400, 60),
    ("SW-CORE", "2960-24TT", 400, 180),
    ("SERVER0", "Server-PT", 620, 180),
    ("SW-ACCOUNTS", "2960-24TT", 150, 320),
    ("SW-HR", "2960-24TT", 400, 320),
    ("SW-IT", "2960-24TT", 650, 320),
    ("ACC-PC1", "PC-PT", 90, 460),
    ("ACC-PC2", "PC-PT", 210, 460),
    ("HR-PC1", "PC-PT", 340, 460),
    ("HR-PC2", "PC-PT", 460, 460),
    ("IT-PC1", "PC-PT", 590, 460),
    ("IT-PC2", "PC-PT", 710, 460),
]

LINKS = [
    ("R1-OMS", "GigabitEthernet0/0", "SW-CORE", "GigabitEthernet0/1"),
    ("SW-CORE", "FastEthernet0/1", "SW-ACCOUNTS", "FastEthernet0/1"),
    ("SW-CORE", "FastEthernet0/2", "SW-HR", "FastEthernet0/1"),
    ("SW-CORE", "FastEthernet0/3", "SW-IT", "FastEthernet0/1"),
    ("SW-CORE", "FastEthernet0/4", "SERVER0", "FastEthernet0"),
    ("SW-ACCOUNTS", "FastEthernet0/2", "ACC-PC1", "FastEthernet0"),
    ("SW-ACCOUNTS", "FastEthernet0/3", "ACC-PC2", "FastEthernet0"),
    ("SW-HR", "FastEthernet0/2", "HR-PC1", "FastEthernet0"),
    ("SW-HR", "FastEthernet0/3", "HR-PC2", "FastEthernet0"),
    ("SW-IT", "FastEthernet0/2", "IT-PC1", "FastEthernet0"),
    ("SW-IT", "FastEthernet0/3", "IT-PC2", "FastEthernet0"),
]

POOLS = [
    ("ACCOUNTS", "192.168.10"),
    ("HR", "192.168.20"),
    ("IT", "192.168.30"),
]


# Canvas area for each row of the index.html table: box corners, then label position.
LABEL_AREAS = {
    "Accounts": ((50, 285, 270, 585), (65, 525)),
    "Human Resources": ((300, 285, 520, 585), (315, 525)),
    "IT": ((550, 285, 770, 585), (565, 525)),
    "Shared Server": ((560, 125, 830, 250), (680, 160)),
}
TITLE_POSITION = (50, 40)


class PageLabels(HTMLParser):
    """Collects the h1/h3 titles and the table rows from index.html."""

    def __init__(self):
        super().__init__()
        self.titles = []
        self.rows = []
        self.tag = None

    def handle_starttag(self, tag, attrs):
        self.tag = tag
        if tag == "tr":
            self.rows.append([])

    def handle_endtag(self, tag):
        self.tag = None

    def handle_data(self, data):
        if self.tag in ("h1", "h3"):
            self.titles.append(data.strip())
        elif self.tag == "td":
            self.rows[-1].append(data.strip())


def add_note(notes, index, position, text):
    note = ET.SubElement(notes, "NOTE", {"uuid": "{%s}" % uuid.uuid5(uuid.NAMESPACE_DNS, f"oms-note-{index}")})
    for tag, value in (
        ("X", position[0]),
        ("Y", position[1]),
        ("Z", 40000 + index),
        ("TEXT", text),
        ("NOTECLUSTERID", "1-1"),
        ("MEM_ADDR", 7000000 + index),
    ):
        ET.SubElement(note, tag).text = str(value)
    note.find("TEXT").set("translate", "true")


def add_box(rectangles, index, corners):
    box = ET.SubElement(rectangles, "RECTANGLE", {"uuid": "{%s}" % uuid.uuid5(uuid.NAMESPACE_DNS, f"oms-box-{index}")})
    for tag, value in zip(("TopLeftX", "TopLeftY", "BottomRightX", "BottomRightY"), corners):
        ET.SubElement(box, tag).text = str(value)
    color = ET.SubElement(box, "Color")
    for channel in ("Red", "Green", "Blue"):
        ET.SubElement(color, channel).text = "0"
    ET.SubElement(box, "Filled", {"OUTLINED": "true", "OUTLINECOLOR": "#000000"}).text = "0"
    ET.SubElement(box, "RECTCLUSTERID").text = "1-1"
    ET.SubElement(box, "MEM_ADDR").text = str(7100000 + index)


def add_page_labels(base, html):
    """Label the topology with the titles and department table from index.html."""
    page = PageLabels()
    page.feed(html)
    rows = [row for row in page.rows if row]
    if {row[0] for row in rows} != set(LABEL_AREAS):
        raise ValueError(f"index.html departments changed: {[row[0] for row in rows]}")

    notes = base.find("PHYSICALWORKSPACE/NOTES")
    rectangles = base.find("RECTANGLES")
    add_note(notes, 0, TITLE_POSITION, "\n".join(page.titles))
    for index, row in enumerate(rows, start=1):
        corners, position = LABEL_AREAS[row[0]]
        add_box(rectangles, index, corners)
        add_note(notes, index, position, "\n".join(row))


def set_text(parent, tag, value):
    element = parent.find(tag)
    if element is None:
        element = ET.SubElement(parent, tag)
    element.text = value


def seed_server_template():
    """The seed is a real 9.0.1 save; its server is cleaner than the bundled one."""
    seed = load_network_seed()
    text = seed.decode("utf-8") if isinstance(seed, bytes) else seed
    for device in re.findall(r"<DEVICE>.*?</DEVICE>", text, re.S):
        if 'model="Server-PT"' in device:
            return device.encode("utf-8")
    raise ValueError("seed network has no Server-PT")


def make_identity_unique(engine, index):
    """Templates repeat one base MAC and serial, which gives every switch the same
    spanning-tree bridge ID and leaves trunks stuck. Each device needs its own."""
    for port in engine.iter("PORT"):
        set_text(port, "BIA", port.findtext("MACADDRESS"))
    for element in engine.iter("BUILD_IN_ADDR"):
        element.text = "0212.00F0.%04X" % index
    if engine.find("SERIALNUMBER") is not None:
        set_text(engine, "SERIALNUMBER", "CAT10106%03d" % index)


def add_startup_config(engine):
    """Mirror the running config so the devices keep it across a reload."""
    for old in engine.findall("STARTUPCONFIG"):
        engine.remove(old)
    startup = ET.SubElement(engine, "STARTUPCONFIG")
    for line in engine.find("RUNNINGCONFIG"):
        ET.SubElement(startup, "LINE").text = line.text


def add_switch_vlans(engine):
    """2960s save VLANs in <VLANS>, not in the running config."""
    vlans = next(engine.iter("VLANS"))
    position = [v.get("number") for v in vlans].index("1") + 1
    for offset, (number, name) in enumerate(VLANS.items()):
        vlan = ET.Element("VLAN", {"name": name, "number": str(number), "rspan": "0"})
        vlans.insert(position + offset, vlan)


def set_pc_dhcp(device):
    engine = device.find("ENGINE")
    port = next(engine.iter("PORT"))
    set_text(port, "PORT_DHCP_ENABLE", "true")
    for tag in ("IP", "SUBNET", "PORT_GATEWAY", "PORT_DNS"):
        set_text(port, tag, None)
    set_text(engine, "GATEWAY", None)
    client = engine.find("DNS_CLIENT")
    if client is not None:
        set_text(client, "SERVER_IP", None)


def add_pool(pools, name, prefix):
    pool = ET.SubElement(pools, "POOL")
    for tag, value in (
        ("NAME", name),
        ("NETWORK", f"{prefix}.0"),
        ("MASK", MASK),
        ("DEFAULT_ROUTER", f"{prefix}.1"),
        ("TFTP_ADDRESS", "0.0.0.0"),
        ("START_IP", f"{prefix}.100"),
        ("END_IP", f"{prefix}.149"),
        ("DNS_SERVER", SERVER_IP),
        ("MAX_USERS", "50"),
        ("DOMAIN_NAME", None),
        ("DHCP_POOL_LEASES", None),
        ("LEASE_TIME", "86400000"),
        ("WLC_ADDRESS", "0.0.0.0"),
    ):
        ET.SubElement(pool, tag).text = value


def configure_server(device, html):
    engine = device.find("ENGINE")
    port = next(engine.iter("PORT"))
    set_text(port, "PORT_DNS", SERVER_IP)
    set_text(engine.find("DNS_CLIENT"), "SERVER_IP", SERVER_IP)

    # Packet Tracer always keeps a default serverPool. It is left holding zero
    # addresses, and VLAN 40 has no DHCP clients, so it never hands out a lease.
    dhcp = next(engine.iter("DHCP_SERVER"))
    set_text(dhcp, "ENABLED", "1")
    pools = dhcp.find("POOLS")
    default = pools.find("POOL")
    set_text(default, "NETWORK", "192.168.40.0")
    set_text(default, "MASK", MASK)
    set_text(default, "START_IP", "192.168.40.0")
    set_text(default, "END_IP", "192.168.40.255")
    set_text(default, "MAX_USERS", "0")
    for name, prefix in POOLS:
        add_pool(pools, name, prefix)

    dns = engine.find("DNS_SERVER")
    set_text(dns, "ENABLED", "1")
    database = dns.find("NAMESERVER-DATABASE")
    record = ET.SubElement(database, "RESOURCE-RECORD")
    for tag, value in (
        ("TYPE", "A-REC"),
        ("NAME", "office.local"),
        ("TTL", "86400"),
        ("IPADDRESS", SERVER_IP),
    ):
        ET.SubElement(record, tag).text = value

    set_text(engine.find("HTTP_SERVER"), "ENABLED", "1")
    pages = [f for f in engine.iter("FILE") if f.findtext("NAME") == "index.html"]
    if len(pages) != 1:
        raise ValueError(f"expected one index.html on the server, found {len(pages)}")
    pages[0].find("FILE_CONTENT/TEXT").text = html


def main():
    models, modules = load_templates()
    models = dict(models)
    models["Server-PT"] = seed_server_template()

    lab = Lab(models=models, modules=modules)
    lab.prune_seed_devices()

    ids = {}
    for name, model, x, y in DEVICES:
        options = {}
        if name in IOS_DEVICES:
            options["ios_config"] = ios_commands(name).split("\n")
        if name == "SERVER0":
            options["pc_ip"] = (SERVER_IP, MASK, SERVER_GATEWAY)
        ids[name] = lab.add_device(model, name, x, y, **options)

    for a, a_port, b, b_port in LINKS:
        lab.link(ids[a], a_port, ids[b], b_port)

    with open(ROOT / "web" / "index.html", encoding="utf-8", newline="") as f:
        html = f.read()

    for index, (name, model, _, _) in enumerate(DEVICES, start=1):
        device = lab._els[ids[name]]
        engine = device.find("ENGINE")
        make_identity_unique(engine, index)
        if name in IOS_DEVICES:
            add_startup_config(engine)
        if model == "2960-24TT":
            add_switch_vlans(engine)
        elif model == "2911":
            # The 2911 template saves its ports powered off; Gi0/0 is the first.
            set_text(next(engine.iter("PORT")), "POWER", "true")
        elif model == "PC-PT":
            set_pc_dhcp(device)
        elif model == "Server-PT":
            configure_server(device, html)

    add_page_labels(lab.base, html)

    lab.save(str(OUTPUT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
