class AP:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.connected_hosts = []

    def connect_host(self, host_id):
        self.connected_hosts.append(host_id)

    def __repr__(self):
        return f"AP({self.name}, X={self.x}, Y={self.y}, Connected Hosts={self.connected_hosts})"

class Host:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.connected_ap = None

    def connect_to_ap(self, ap_id):
        self.connected_ap = ap_id

    def __repr__(self):
        return f"Host({self.name}, X={self.x}, Y={self.y}, Connected AP={self.connected_ap})"

# 实例化AP和Host对象
APs = {
    "AP1": AP("AP1", 100, 200),
    "AP2": AP("AP2", 150, 250)
}

Hosts = {
    1: Host("Host1", 105, 205),
    2: Host("Host2", 110, 210),
    3: Host("Host3", 115, 215),
    4: Host("Host4", 155, 255),
    5: Host("Host5", 160, 260)
}

# 建立连接
APs["AP1"].connect_host(1)
APs["AP1"].connect_host(2)
APs["AP1"].connect_host(3)
APs["AP2"].connect_host(4)
APs["AP2"].connect_host(5)

Hosts[1].connect_to_ap("AP1")
Hosts[2].connect_to_ap("AP1")
Hosts[3].connect_to_ap("AP1")
Hosts[4].connect_to_ap("AP2")
Hosts[5].connect_to_ap("AP2")

# 打印结构以验证
print(APs)
print(Hosts)
