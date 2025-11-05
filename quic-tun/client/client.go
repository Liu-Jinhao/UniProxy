package client

import (
	"context"
	"crypto/tls"
	"fmt"
	"io"
	"net"
	"strconv"
	"strings"

	"golang.org/x/sys/unix"
	"github.com/kungze/quic-tun/pkg/constants"
	"github.com/kungze/quic-tun/pkg/log"
	"github.com/kungze/quic-tun/pkg/token"
	"github.com/kungze/quic-tun/pkg/tunnel"
	quic "github.com/qdeconinck/mp-quic"
)

type ClientEndpoint struct {
	LocalSocket          string
	ServerEndpointSocket string
	TokenSource          token.TokenSourcePlugin
	TlsConfig            *tls.Config
}

func (c *ClientEndpoint) Start() {
	cfgServer := &quic.Config{
		KeepAlive:   true,
		CreatePaths: true,
	}
	// Dial server endpoint
	session, err := quic.DialAddr(c.ServerEndpointSocket, c.TlsConfig, cfgServer)
	if err != nil {
		panic(err)
	}
	parent_ctx := context.WithValue(context.TODO(), constants.CtxRemoteEndpointAddr, session.RemoteAddr().String())
	// Listen on a TCP socket, wait client application's connection request.
	localSocket := strings.Split(c.LocalSocket, ":")
	port, err := strconv.Atoi(localSocket[2])
	if err != nil {
		panic(err)
	}
	listener, err := net.ListenTCP(strings.ToLower(localSocket[0]), &net.TCPAddr{IP: net.ParseIP(localSocket[1]), Port: port})
	if err != nil {
		panic(err)
	}
	defer listener.Close()

	// Get the syscall.RawConn from the TCPListener
	rawConn, err := listener.SyscallConn()
	if err != nil {
		panic(err)
	}

	// Set the socket option
	err = rawConn.Control(func(fd uintptr) {
		err = unix.SetsockoptInt(int(fd), unix.SOL_IP, unix.IP_TRANSPARENT, 1)
	})
	if err != nil {
		panic(err)
	}

	err = rawConn.Control(func(fd uintptr) {
		err = unix.SetsockoptInt(int(fd), unix.SOL_SOCKET, unix.SO_REUSEADDR, 1)
	})
	if err != nil {
		panic(err)
	}

	err = rawConn.Control(func(fd uintptr) {
		err = unix.SetsockoptInt(int(fd), unix.SOL_SOCKET, unix.SO_REUSEPORT, 1)
	})
	if err != nil {
		panic(err)
	}

	log.Infow("Client endpoint start up successful", "listen address", listener.Addr())
	for {
		// Accept client application connectin request
		conn, err := listener.Accept()
		if err != nil {
			log.Errorw("Client app connect failed", "error", err.Error())
		} else {
			logger := log.WithValues(constants.ClientAppAddr, conn.RemoteAddr().String())
			//logger.Info("Client connection accepted, prepare to entablish tunnel with server endpint for this connection.")
			go func() {
				defer func() {
					conn.Close()
					//logger.Info("Tunnel closed")
				}()
				// Open a quic stream for each client application connection.
				stream, err := session.OpenStreamSync()
				stream.SetTCPConn(&conn)
				if err != nil {
					logger.Errorw("Failed to open stream to server endpoint.", "error", err.Error())
					return
				}
				defer stream.Close()
				logger = logger.WithValues(constants.StreamID, stream.StreamID())
				// Create a context argument for each new tunnel
				ctx := context.WithValue(
					logger.WithContext(parent_ctx),
					constants.CtxClientAppAddr, conn.RemoteAddr().String())
				hsh := tunnel.NewHandshakeHelper(constants.TokenLength, handshake)
				c.TokenSource = token.NewFixedTokenPlugin("tcp:" + conn.LocalAddr().String())
				hsh.TokenSource = &c.TokenSource
				// Create a new tunnel for the new client application connection.
				tun := tunnel.NewTunnel(&stream, constants.ClientEndpoint)
				tun.Conn = &conn
				tun.Hsh = &hsh
				if !tun.HandShake(ctx) {
					return
				}
				tun.Establish(ctx)
			}()
		}
	}
}

func handshake(ctx context.Context, stream *quic.Stream, hsh *tunnel.HandshakeHelper) (bool, *net.Conn) {
	logger := log.FromContext(ctx)
	//logger.Info("Starting handshake with server endpoint")
	token, err := (*hsh.TokenSource).GetToken(fmt.Sprint(ctx.Value(constants.CtxClientAppAddr)))
	if err != nil {
		logger.Errorw("Encounter error.", "erros", err.Error())
		return false, nil
	}
	hsh.SetSendData([]byte(token))
	_, err = io.CopyN(*stream, hsh, constants.TokenLength)
	if err != nil {
		logger.Errorw("Failed to send token", err.Error())
		return false, nil
	}
	_, err = io.CopyN(hsh, *stream, constants.AckMsgLength)
	if err != nil {
		logger.Errorw("Failed to receive ack", err.Error())
		return false, nil
	}
	switch hsh.ReceiveData[0] {
	case constants.HandshakeSuccess:
		//logger.Info("Handshake successful")
		return true, nil
	case constants.ParseTokenError:
		logger.Errorw("handshake error!", "error", "server endpoint can not parser token")
		return false, nil
	case constants.CannotConnServer:
		logger.Errorw("handshake error!", "error", "server endpoint can not connect to server application")
		return false, nil
	default:
		logger.Errorw("handshake error!", "error", "received an unknow ack info")
		return false, nil
	}
}
