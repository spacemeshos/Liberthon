import docker
import time
import tools
import random
import os
import pprint
from random import SystemRandom
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait, as_completed

### Create docker client

pp = pprint.PrettyPrinter(indent=4)

randcon = 8

client = docker.from_env()
advclient = docker.APIClient(base_url='unix://var/run/docker.sock')

tools.cleanUp(client.containers.list())

time.sleep(1)
print "Creating bootstrap container"
bootstrap = client.containers.run("spaceanton/spacemesh:spacemesh_p2p", detach=True, ports={9090:9999}, environment={"BOOTPARAMS": "--gossip --randcon 3 --bucketsize 100"})
print "Waiting for node to boot up"
tools.waitForRPC(bootstrap)
tools.registerProtocol(advclient, bootstrap, "gossip_test", 8081)


# collect id and ip.

bootIP = tools.getExternalIP(advclient, bootstrap)
bootID = tools.getPublicKey(bootstrap)

print "Bootnode is at - "+ bootstrap.name + ": " + bootIP + ":7513/" + bootID

# Start a network with size `netsize` boot each client and add to the list
# After that run the needed tests.
netsize = 30
idxes = {}
contlist = []


def createNodes(netsize, bootIP, bootID):
    for i in range(netsize):
        node = client.containers.run("spaceanton/spacemesh:spacemesh_p2p", detach=True, ports={"9090": None}, environment={"BOOTPARAMS": "--bootstrap --gossip --randcon " + str(randcon) + " --bucketsize 20 --bootnodes \"" + bootIP + ":7513/" + bootID + "\""})
        contlist.append({"cont": node})
        idxes[node.name] = i


def runMultiple(func, afterfunc):
    futures = []
    with ProcessPoolExecutor(max_workers=10) as pool:
        # this code will run in multiple threads
        for cont in contlist:
            fut = pool.submit(func, cont["cont"].name)
            futures.append(fut)
    # As the jobs are completed, we process the data more
    for res in as_completed(futures):
        if afterfunc != None:
            if isinstance(afterfunc, list):
                # a list of function    
                for f in range(afterfunc):
                    f(res.result())
            elif callable(afterfunc):
                    afterfunc(res.result())

def getpubkey(cont):
    id = tools.getPublicKey(client.containers.get(cont))
    return True, cont, id

def assignpubkey(packed):
    suc, cont, id = packed
    contlist[idxes[cont]]["id"] = id

createNodes(netsize, bootIP, bootID)
runMultiple(getpubkey, assignpubkey)

for cont in contlist:
    assert "id" in cont

print "Spinned up " + str(netsize) + " more instances booting from bootnode"

def waitForNeighborhood(cont):
    selected = False
    selectcount = 0
    selectedArr = []
    line = "Neighborhood initialized"
    print "[" + cont + "]"
    start_time = time.time()
    for i in client.containers.get(cont).logs(stream=True, stdout=True):
        elapsed_time = time.time() - start_time
        if line in i or selected:
            if not selected:
                print "found neighbors"
                # switch to selected
                return True

        if elapsed_time >= 60 * randcon:
            print "time passed :( for " + cont
            return False
    return False


runMultiple(waitForNeighborhood, None)


for cont in contlist:
    tools.waitForRPC(cont["cont"])
    tools.registerProtocol(advclient, cont["cont"], "gossip_test", 8081)


print " Broadcasting a gossip message ! "


def waitForGossipMessage(cont):
    line = "Got gossip message!"
    print "[" + cont + "]"
    start_time = time.time()
    for i in client.containers.get(cont).logs(stream=True, stdout=True):
        elapsed_time = time.time() - start_time
        if line in i:
            print "I got it !"
            return True
        if elapsed_time > 60 * randcon:
            return False

counting = 0
def count(success):
    if success:
        global counting
        counting = counting + 1 


cryptogen = SystemRandom()
num = cryptogen.randrange(len(contlist))
broadcaster = contlist[num]
tools.broadcast(advclient, broadcaster["cont"], "gossip_test", "Hello!")
contlist.remove(broadcaster)

runMultiple(waitForGossipMessage, count)

print str(counting) + " nodes got the gossip message"

print "Starting to shutdown nodes"

contlist.append({ "cont": bootstrap })
contlist.append({ "cont": broadcaster["cont"] })

tools.cleanUp(contlist)


