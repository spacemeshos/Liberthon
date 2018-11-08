# Liberthon

## Liberthon Hackathon
Welcome to the Liberthon Hackathon toolset created especially to provide you with P2P capabilities 

### <b>Quickstrat: Running Spacemesh P2P client</b>
You can deploy the P2P client in two ways:
- Compile spacemesh agent and run executable locally
- Build or use Spacemesh Docker image

### Building spacemesh agent
Pre requisites: install the go framework
```
go get github.com/spacemeshos/go-spacemesh
cd ~/go/src/github/spacemeshos/go-spacemesh
git checkout -b hackathon
go build
```
### Using Spacemsh P2P
Whether you are running the agent via Docker or Executable, This is how you can communicate and use the agent to build a P2P network.

In order for us to setup a P2P network we must first boot up a bootstrap node, This node will be one of the first nodes any client will connect to and allow nodes to discover new nodes in the network. to boot up a bootstrap node use:
```
./go-spacemesh
```
After a bootstrap node has been created, the other nodes can be booted and configured to connect to it.
To specify a bootstrap when booting more nodes use the following command:

```
./go-spacemesh --bootstrap --bootnodes <BOOTSTRAP_IP>:<PORT<7513>>/<BOOTSTRAP_NODEID>
```
Note that you need to have the node ID in order to connect

## spacemesh P2P image

```
docker run spaceanton/spacemesh:spacemesh_p2p
```

you can expose RPC port 9090 to control from host or integrate you executable to the docker image itself

## Using the P2P framework
After setting up your enviorment you can communicate with the p2p agent to send and receive messages.

### Receiving messages
In order to receive messages from the agent, a UDP por can be opened for listening to new messages. To open a UDP port a register command must be sent to the agent in the following manner:
```
curl -X POST -d '{ "name":"anton", "port":8081 }' 127.0.0.1:9090/v1/register
```
* `name`: The P2P inner protocol uses a protocol name to distinguish between messages of diffrent protocols. 
* `port`: The port number on which data will be received (UDP) 

After registering your protocol, raw messages can be received on the port. <b>note:</b> the data received is binary and needs to be parsed by your app according to your protocol.

### Sending messages
Send a message to a specific P2P client
```
curl -X POST -d '{ "nodeID":"vx3xRTWPhSapZPB7oTCCD3J8hNrWzFmzQwnzut7BNLMV", "protocolName": "anton", "payload" : [0,10,10,10] }' 127.0.0.1:9090/v1/send
```
This call is similar to the brodcast call
- `nodeID`: ID of the receiver node 

### Broadcasting messages
Messages can be sent throughout the network thru the gossip network, to send a message use the following call:
```
curl -X POST -d '{ "protocolName": "anton", "payload" : [0,10,10,10] }' 127.0.0.1:9090/v1/broadcast
```
- `protocolName`: protocol name that will be sent, receiveing clients will route the message according to this name
- `payload`: the payload (in bytes) that contains your application specific data.

## Using the python `devnet` script
the devnet is a simple python script used to spin up local docker containers to simulate a network.
settings like size of the network and amount of connections each node holds are determined in the script code before running.

`python devnet.py`

This script tests a simple message broadcast but it can be extended to test much more than that.
