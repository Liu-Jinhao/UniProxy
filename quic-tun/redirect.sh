#iptables -t nat -F
#iptables -t nat -N redirect
#iptables -t nat -A redirect -p tcp -j REDIRECT --to-port=6500
#iptables -t nat -A PREROUTING --in-interface r1-eth0 -j redirect

ip rule add fwmark 1 table 100
ip route add local 0.0.0.0/0 dev lo table 100
iptables -t mangle -A PREROUTING --in-interface r1-eth0 -p tcp -d 10.0.7.0/24 -j TPROXY --on-port 6500 --on-ip 127.0.0.1 --tproxy-mark 1/1
