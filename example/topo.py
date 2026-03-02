from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel

if '__main__' == __name__:
    setLogLevel('info')
    net = Mininet(link=TCLink)  

    h1 = net.addHost('h1') # client
    h2 = net.addHost('h2') # server
    r1 = net.addHost('r1') # client-side proxy
    r2 = net.addHost('r2')
    r3 = net.addHost('r3')
    r4 = net.addHost('r4')
    r5 = net.addHost('r5') # server-side proxy
    

    net.addLink(h1, r1)
    net.addLink(r1, r2)
    net.addLink(r1, r3)
    net.addLink(r2, r4)
    net.addLink(r3, r4)
    net.addLink(r4, r5)
    net.addLink(r5, h2)
    net.build()

    h1.cmd("ifconfig h1-eth0 0")

    r1.cmd("ifconfig r1-eth0 0")
    r1.cmd("ifconfig r1-eth1 0")
    r1.cmd("ifconfig r1-eth2 0")

    r2.cmd("ifconfig r2-eth0 0")
    r2.cmd("ifconfig r2-eth1 0")

    r3.cmd("ifconfig r3-eth0 0")
    r3.cmd("ifconfig r3-eth1 0")

    r4.cmd("ifconfig r4-eth0 0")
    r4.cmd("ifconfig r4-eth1 0")
    r4.cmd("ifconfig r4-eth2 0")

    r5.cmd("ifconfig r5-eth0 0")
    r5.cmd("ifconfig r5-eth1 0")

    h2.cmd("ifconfig h2-eth0 0")


    r1.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
    r2.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
    r3.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
    r4.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
    r5.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")


    h1.cmd("ifconfig h1-eth0 10.0.0.1 netmask 255.255.255.0")

    r1.cmd("ifconfig r1-eth0 10.0.0.2 netmask 255.255.255.0")
    r1.cmd("ifconfig r1-eth1 10.0.1.1 netmask 255.255.255.0")
    r1.cmd("ifconfig r1-eth2 10.0.2.1 netmask 255.255.255.0")

    r2.cmd("ifconfig r2-eth0 10.0.1.2 netmask 255.255.255.0")
    r2.cmd("ifconfig r2-eth1 10.0.4.1 netmask 255.255.255.0")

    r3.cmd("ifconfig r3-eth0 10.0.2.2 netmask 255.255.255.0")
    r3.cmd("ifconfig r3-eth1 10.0.5.1 netmask 255.255.255.0")

    r4.cmd("ifconfig r4-eth0 10.0.4.2 netmask 255.255.255.0")
    r4.cmd("ifconfig r4-eth1 10.0.5.2 netmask 255.255.255.0")
    r4.cmd("ifconfig r4-eth2 10.0.6.1 netmask 255.255.255.0")

    r5.cmd("ifconfig r5-eth0 10.0.6.2 netmask 255.255.255.0")
    r5.cmd("ifconfig r5-eth1 10.0.7.1 netmask 255.255.255.0")

    h2.cmd("ifconfig h2-eth0 10.0.7.2 netmask 255.255.255.0")


    h1.cmd("ip route flush table main")
    h1.cmd("ip route add 10.0.0.0/24 dev h1-eth0 scope link")
    h1.cmd("ip route add default via 10.0.0.2 dev h1-eth0")


    r1.cmd("ip rule add from 10.0.0.2 table 1")
    r1.cmd("ip rule add from 10.0.1.1 table 2")
    r1.cmd("ip rule add from 10.0.2.1 table 3")

    r1.cmd("ip route add 10.0.0.0/24 dev r1-eth0 scope link table 1")
    r1.cmd("ip route add default via 10.0.0.1 dev r1-eth0 table 1")

    r1.cmd("ip route add 10.0.1.0/24 dev r1-eth1 scope link table 2")
    r1.cmd("ip route add default via 10.0.1.2 dev r1-eth1 table 2")

    r1.cmd("ip route add 10.0.2.0/24 dev r1-eth2 scope link table 3")
    r1.cmd("ip route add default via 10.0.2.2 dev r1-eth2 table 3")

    r1.cmd("ip route add 10.0.0.0/24 dev r1-eth0 scope link")
    r1.cmd("ip route add 10.0.1.0/24 dev r1-eth1 scope link")
    r1.cmd("ip route add 10.0.2.0/24 dev r1-eth2 scope link")
    r1.cmd("ip route add 10.0.4.0/24 via 10.0.1.2 dev r1-eth1")
    r1.cmd("ip route add 10.0.5.0/24 via 10.0.2.2 dev r1-eth2")
    
    r1.cmd("ip route add default via 10.0.1.2 dev r1-eth1")


    r2.cmd("ip route add 10.0.1.0/24 dev r2-eth0 scope link")
    r2.cmd("ip route add 10.0.4.0/24 dev r2-eth1 scope link")
    r2.cmd("ip route add 10.0.0.0/24 via 10.0.1.1 dev r2-eth0")
    r2.cmd("ip route add 10.0.2.0/24 via 10.0.1.1 dev r2-eth0")
    r2.cmd("ip route add 10.0.3.0/24 via 10.0.1.1 dev r2-eth0")
    r2.cmd("ip route add 10.0.5.0/24 via 10.0.4.2 dev r2-eth1")
    r2.cmd("ip route add 10.0.6.0/24 via 10.0.4.2 dev r2-eth1")
    r2.cmd("ip route add 10.0.7.0/24 via 10.0.4.2 dev r2-eth1")
    r2.cmd("ip route add default via 10.0.4.2 dev r2-eth1")

    
    r3.cmd("ip route add 10.0.2.0/24 dev r3-eth0 scope link")
    r3.cmd("ip route add 10.0.5.0/24 dev r3-eth1 scope link")
    r3.cmd("ip route add 10.0.0.0/24 via 10.0.2.1 dev r3-eth0")
    r3.cmd("ip route add 10.0.1.0/24 via 10.0.2.1 dev r3-eth0")
    r3.cmd("ip route add 10.0.3.0/24 via 10.0.2.1 dev r3-eth0")
    r3.cmd("ip route add 10.0.4.0/24 via 10.0.5.2 dev r3-eth1")
    r3.cmd("ip route add 10.0.6.0/24 via 10.0.5.2 dev r3-eth1")
    r3.cmd("ip route add 10.0.7.0/24 via 10.0.5.2 dev r3-eth1")
    r3.cmd("ip route add default via 10.0.5.2 dev r3-eth1")

    
    r5.cmd("ip route add 10.0.6.0/24 dev r5-eth0 scope link")
    r5.cmd("ip route add 10.0.7.0/24 dev r5-eth1 scope link")
    r5.cmd("ip route add default via 10.0.6.1 dev r5-eth0")

    
    r4.cmd("ip route add 10.0.4.0/24 dev r4-eth0 scope link")
    r4.cmd("ip route add 10.0.5.0/24 dev r4-eth1 scope link")
    r4.cmd("ip route add 10.0.6.0/24 dev r4-eth2 scope link")
   
    r4.cmd("ip route add 10.0.0.0/24 via 10.0.4.1 dev r4-eth0")
    r4.cmd("ip route add 10.0.1.0/24 via 10.0.4.1 dev r4-eth0")
    r4.cmd("ip route add 10.0.2.0/24 via 10.0.5.1 dev r4-eth1")
    r4.cmd("ip route add default via 10.0.6.2 dev r4-eth2")

    h2.cmd("ip route add 10.0.7.0/24 dev h2-eth0 scope link")
    h2.cmd("ip route add default via 10.0.7.1 dev h2-eth0")
    
    
    r2.cmd("tc qdisc add dev r2-eth0 root handle 1: netem delay 5ms")
    r2.cmd("tc qdisc add dev r2-eth1 root handle 1: netem delay 5ms")
    
    r1.cmd("tc qdisc add dev r1-eth1 root cake bandwidth 100mbit besteffort flowblind")
    r4.cmd("tc qdisc add dev r4-eth0 root cake bandwidth 100mbit besteffort flowblind")
    
    r3.cmd("tc qdisc add dev r3-eth0 root handle 1: netem delay 5ms")
    r3.cmd("tc qdisc add dev r3-eth1 root handle 1: netem delay 5ms")

    r1.cmd("tc qdisc add dev r1-eth2 root cake bandwidth 50mbit besteffort flowblind")
    r4.cmd("tc qdisc add dev r4-eth1 root cake bandwidth 50mbit besteffort flowblind")

    CLI(net)
    net.stop()
