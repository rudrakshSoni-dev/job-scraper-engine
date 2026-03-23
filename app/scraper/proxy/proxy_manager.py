import random


class ProxyManager:
    def __init__(self):
        self.proxies = [
            {
                "server": "http://username:password@host:port"
            },
            # add more later
        ]

    def get_proxy(self):
        return random.choice(self.proxies)