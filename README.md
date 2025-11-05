# UniProxy

## How to use UniProxy

Run `go build` in `./quic-tun/client/cmd` and `./quic/tun/server/cmd` to compile the client- and server-side proxy program, respectively.

At the server-side proxy, run:

    ./quic-tun/server/cmd --listen-on 10.0.6.2:7500

The address of the server-side proxy is *10.0.6.2:7500*.

At the client-side proxy, run `client.sh`, which includes:

    ./quic-tun/client/cmd/cmd --listen-on tcp:127.0.0.1:6500 --server-endpoint 10.0.6.2:7500
    ip rule add fwmark 1 table 100
    ip route add local 0.0.0.0/0 dev lo table 100
    iptables -t mangle -A PREROUTING --in-interface r1-eth0 -p tcp -d 10.0.7.0/24 -j TPROXY --on-port 6500 --on-ip 127.0.0.1 --tproxy-mark 1/1
    
The client-side proxy is listening on *127.0.0.1:6500*. The `iptables` command and the corrsponding routing commands intercepts tcp packets that enter through *r1-eth0* interface and have a destination IP within the *10.0.7.0/24* subnet, and redirects them to the client-side proxy's listening port.  The `iptables` command can be modified according to specific needs.

If you want to change the scheduling algorithm, you can modify the parameter *SCHE_ALGO* in `./mp-quic/scheduler.go`. If you want to change the receive window size, you can modify the parameter *InitialConnectionFlowControlWindow* in `./mp-quic/internal/protocol/protocol.go` and the parameters *ReceiveConnectionFlowControlWindow*, *DefaultMaxReceiveConnectionFlowControlWindowServer*, *DefaultMaxReceiveConnectionFlowControlWindowClient* in `./mp-quic/internal/protocol/server_parameters.go`. After modifying the above parameters, you need to recompile the proxy program to make the changes take effect.

## Key implementation in UniProxy

We implement the function *adjustAllocation* at line 559 in `./mp-quic/scheduler.go` to adjust the stream-to-path assignment.

We implement the function *TokenRoundRobinIterate* at line 277 in `./mp-quic/scheduler.go` to perform TRR scheduling. It calls the function *getStreamForPath* to get the stream for sending data over the currently scheduled path. We also implement the function *distributeToken* to distribute tokens to streams in a Round-Robin manner.