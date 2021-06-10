"""
a coredns module for redis plugin (from jumpscale tfgatway tool)

only supports CNAME records
"""
import json
import redis

from .helpers import Factory


DEFAULT_REDIS_HOST = "localhost"
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_PASSWORD = None


class RedisFactory(Factory):
    def create(self, *args):
        host, port, password = args
        return redis.Redis(host, port, password=password)


redis_factory = RedisFactory()


def get_redis(options):
    host = options.get("host", DEFAULT_REDIS_HOST)
    port = options.get("port", DEFAULT_REDIS_PORT)
    password = options.get("password", DEFAULT_REDIS_PASSWORD)
    return redis_factory.get(host, port, password)


class CoreDNS:
    def __init__(self, domain, options):
        self.domain = domain.strip()

        options = options.get("coredns", {})
        self.redis = get_redis(options)

    def _get_domain(self, prefix):
        if prefix:
            domain = f"{prefix}.{self.domain}"
        else:
            domain = self.domain

        if not domain.endswith("."):
            domain += "."

        return domain.lower()

    def _read_records(self, subdomain, domain):
        subdomain = subdomain.lower()
        if self.redis.hexists(domain, subdomain):
            return json.loads(self.redis.hget(domain, subdomain))
        return {}

    def _write_records(self, subdomain, domain, data):
        self.redis.hset(domain, subdomain.lower(), json.dumps(data))

    def create(self, subdomain="", prefix="", record_type="a", records=None):
        """
        registers a subdomain record with the given type
        for every entry you need to comply with record format

        Args:
            subdomain (str, optional): sub-domain, e,g. marketplace. Defaults to "".
            prefix (str, optional): main domain prefix if any. Defaults to "".
            record_type (str, optional): record type. Defaults to "a".
            records ([type], optional): records of that type. Defaults to None.
        """
        records = records or []

        domain = self._get_domain(prefix)
        data = self._read_records(subdomain, domain)

        if record_type in data:
            for record in data[record_type]:
                if record not in records:
                    records.append(record)

        data[record_type] = records
        self._write_records(subdomain, domain, data)

    def delete(self, subdomain, prefix, record_type):
        domain = self._get_domain(prefix)
        data = self._read_records(subdomain, domain)

        if record_type in data:
            del data[record_type]

        self._write_records(subdomain, domain, data)

    def create_cname_record(self, subdomain, prefix, points_to):
        """
        registers a sub-domain CNAME record

        Args:
            subdomain (str): subdomain, e.g. abdo
            prefix (str, optional): main domain prefix if any. Defaults to "".
            points_to (str): the host it points to
        """
        self.create(subdomain, record_type="cname", prefix=prefix, records=[{"host": points_to}])

    def delete_cname_record(self, subdomain, prefix):
        self.delete(subdomain, prefix, record_type="cname")
