import sys
import requests

def getRPCPort(advclient, cont):
    inspect = advclient.inspect_container(cont.name)
    rpcport = inspect['NetworkSettings']['Ports']['9090/tcp'][0]['HostPort']
    return rpcport

def waitForRPC(cont):
    for l in cont.logs(stream=True, stdout=True):
        if "Started GRPC" in l:
            return

def registerProtocol(advclient, cont, proto, port):
    rpcport = getRPCPort(advclient, cont)
    print "Register on " + "http://127.0.0.1:" + str(rpcport) + "/v1/register"
    r = requests.post("http://127.0.0.1:" + str(rpcport) + "/v1/register", json={ "name": proto, "port": port })
    print("Registerd protocol response ", r.status_code, r.reason, r.text)


def broadcast(advclient, cont, proto, message):
    rpcport = getRPCPort(advclient, cont)
    print "Sending message to " + "http://127.0.0.1:" + str(rpcport) + "/v1/broadcast"
    r = requests.post("http://127.0.0.1:" + str(rpcport) + "/v1/broadcast", json={ "protocolName": proto, "payload": [10, 10, 10] })
    print("Send broadcast, response ", r.status_code, r.reason, r.text)

def getExternalIP(advclient, cont):
    ip = ""
    nets = advclient.inspect_container(cont.name)['NetworkSettings']['Networks']
    for net in nets:
        ip = nets[net]["IPAddress"]
        if ip is not "":
            print ip
            break
    return ip

def getPublicKey(cont):
    id = ""
    for l in cont.logs(stream=True, stdout=True):
        if "identity" in l:
            id = l.split('>>')[1].strip()
            break
    return id

def cleanUp(contlist):
    ### Kill all dockers with nice bar
    toolbar_width = len(contlist)
    print "Killing all dockers"
    sys.stdout.write("[%s]" % (" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['
    for i in contlist:
        cont = i
        if isinstance(i, dict):
            cont = cont["cont"]
        cont.kill()
        # update the bar
        sys.stdout.write("-")
        sys.stdout.flush()
    sys.stdout.write("\n")