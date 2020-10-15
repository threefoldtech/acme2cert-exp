"""
a coredns module for redis plugin (from jumpscale tfgatway tool)

only supports A and CNAME records for now
"""
import json
import redis

from ipaddress import IPv4Address, IPv6Address, AddressValueError


def check_address(addr):
    try:
        return IPv4Address(addr)
    except AddressValueError:
        raise ValueError(f"'{addr}' is not a valid IPv4 address")

    try:
        return IPv6Address(addr)
    except:
        raise ValueError(f"'{addr}' is not a valid IPv6 address")


class CoreDNS:

    def __init__(self, domain, redis):
        self.domain = domain.strip()
        self.redis = redis

        if not self.domain.endswith("."):
            self.domain += "."

    @classmethod
    def from_redis(cls, domain, host='localhost', port=6379, password=None):
        return cls(domain, redis.Redis(host=host, port=port, password=password))

    def register(self, subdomain="", record_type="a", records=None):
        """
        registers a subdomain record with the given type
        for every entry you need to comply with record format

        Args:
            subdomain (str, optional): sub-domain, e,g. marketplace. Defaults to "".
            record_type (str, optional): record type. Defaults to "a".
            records ([type], optional): records of that type. Defaults to None.
        """
        data = {}
        records = records or []
        if self.redis.hexists(self.domain, subdomain):
            data = json.loads(self.redis.hget(self.domain, subdomain))
        if record_type in data:
            records.extend(data[record_type])
        data[record_type] = records
        self.redis.hset(self.domain, subdomain, json.dumps(data))

    def register_a_record(self, subdomain, record_ip):
        """
        registers a sub-domain A record

        Args:
            subdomain (str): e.g. abdo
            record_ip (str): ip address

        Raises:
            ValueError: in case `record_ip` is not valid
        """
        check_address(record_ip)
        return self.register(subdomain, record_type="a", records=[{"ip": record_ip}])

    def register_cname_record(self, subdomain, points_to):
        """
        registers a sub-domain CNAME record

        Args:
            subdomain (str): subdomain, e.g. abdo
            points_to (str): the host it points to

        Returns:
            [type]: [description]
        """
        self.register(subdomain, record_type="cname", records=[{"host": points_to}])
