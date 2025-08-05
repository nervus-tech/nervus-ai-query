import requests
import json
import time
import logging
from threading import Thread
import os

logger = logging.getLogger(__name__)

class EurekaClient:
    def __init__(self, service_name, host_name, port, eureka_url):
        self.service_name = service_name
        self.host_name = host_name
        self.port = port
        self.eureka_url = eureka_url
        self.heartbeat_thread = None

    def register_with_eureka(self):
        """Register service with Eureka"""
        try:
            eureka_data = {
                "instance": {
                    "hostName": self.host_name,
                    "app": self.service_name,
                    "ipAddr": self.host_name,
                    "status": "UP",
                    "overriddenstatus": "UNKNOWN",
                    "port": {
                        "$": self.port,
                        "@enabled": "true"
                    },
                    "securePort": {
                        "$": 443,
                        "@enabled": "false"
                    },
                    "countryId": 1,
                    "dataCenterInfo": {
                        "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                        "name": "MyOwn"
                    },
                    "leaseInfo": {
                        "renewalIntervalInSecs": 30,
                        "durationInSecs": 90,
                        "registrationTimestamp": 0,
                        "lastRenewalTimestamp": 0,
                        "evictionTimestamp": 0,
                        "serviceUpTimestamp": 0
                    },
                    "metadata": {
                        "@class": "java.util.Collections$EmptyMap"
                    },
                    "homePageUrl": f"http://{self.host_name}:{self.port}/",
                    "statusPageUrl": f"http://{self.host_name}:{self.port}/health",
                    "healthCheckUrl": f"http://{self.host_name}:{self.port}/health",
                    "vipAddress": self.service_name,
                    "secureVipAddress": self.service_name,
                    "isCoordinatingDiscoveryServer": "false",
                    "lastUpdatedTimestamp": "0",
                    "lastDirtyTimestamp": "0",
                    "actionType": "ADDED"
                }
            }

            response = requests.post(f"{self.eureka_url}/eureka/apps/{self.service_name}",
                                    json=eureka_data,
                                    headers={"Content-Type": "application/json"})

            if response.status_code == 204:
                logger.info(f"Successfully registered with Eureka at {self.eureka_url}")
                return True
            else:
                logger.error(f"Failed to register with Eureka: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error registering with Eureka: {e}")
            return False

    def heartbeat_eureka(self):
        """Send heartbeat to Eureka"""
        while True:
            try:
                response = requests.put(f"{self.eureka_url}/eureka/apps/{self.service_name}/{self.host_name}")
                if response.status_code != 200:
                    logger.warning(f"Heartbeat failed: {response.status_code}")
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
            time.sleep(30)

    def start_heartbeat(self):
        """Start the heartbeat thread"""
        self.heartbeat_thread = Thread(target=self.heartbeat_eureka, daemon=True)
        self.heartbeat_thread.start()
        logger.info("Started Eureka heartbeat thread")

def create_eureka_client():
    """Factory function to create Eureka client with environment variables"""
    service_name = os.getenv("SERVICE_NAME", "AI-QUERY")
    host_name = os.getenv("HOST_NAME", "ai-query-staging")
    port = int(os.getenv("SERVICE_PORT", "8000"))
    eureka_url = os.getenv("EUREKA_URL", "http://eureka:8761")

    return EurekaClient(service_name, host_name, port, eureka_url) 