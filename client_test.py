import os
from os.path import abspath

import self as self

import hazelcast
import logging
import random
import time

from hazelcast.discovery import HazelcastCloudDiscovery
from tests.hzrc.client import HzRemoteController
from tests.hzrc.ttypes import CloudCluster

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    uri = "https://uat.hazelcast.cloud"
    api_key = "cJvW2fu2InIjkJyvzdp2RPeaF"
    api_secret = "WJvVV0MKYqc1KJejOm8dNGkbhCOipbaSk42l495YnXWx6bgIJgly42XvScQQ"
    rc = HzRemoteController("127.0.0.1", 9701)
    rc.login(uri, api_key, api_secret)
    cluster: CloudCluster = rc.getCluster("1348")
    #rc.scaleUpDownStandardCluster(cluster.id, 2)
    #rc.scaleUpDownStandardCluster(cluster.id, -2)
    #rc.stopCluster(cluster.id)
    #cluster = rc.resumeCluster(cluster.id)
    print(getattr(cluster, "nameForConnect"))

    logging.basicConfig(level=logging.INFO)
    HazelcastCloudDiscovery._CLOUD_URL_BASE = "uat.hazelcast.cloud"
    client = hazelcast.HazelcastClient(
        cluster_name=cluster.nameForConnect,
        cloud_discovery_token=cluster.token,
        statistics_enabled=True,
        ssl_enabled=True,
        ssl_cafile=abspath(os.path.join(cluster.certificatePath + "\\ca.pem")),
        ssl_certfile=abspath(os.path.join(cluster.certificatePath + "\\cert.pem")),
        ssl_keyfile=abspath(os.path.join(cluster.certificatePath + "\\key.pem")),
        ssl_password=cluster.tlsPassword,
    )

    my_map = client.get_map("map").blocking()
    my_map.put("key", "value")

    if my_map.get("key") == "value":
        print("Successful connection!")
        print("Starting to fill the map with random entries.")

        while True:
            random_key = random.randint(1, 100000)
            try:
                my_map.put("key" + str(random_key), "value" + str(random_key))
            except:
                logging.exception("Put operation failed!")

            if random_key % 100 == 0:
                map_size = my_map.size()
                print(f"Current map size: {map_size}")
                time.sleep(1)
    else:
        client.shutdown()
        raise Exception("Connection failed, check your configuration.")
