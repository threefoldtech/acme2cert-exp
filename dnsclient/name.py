from namecom import Name

from .exceptions import DnsConfigError
from .helpers import Factory

class NameFactory(Factory):
    def create(self, *args):
        return Name(*args)


class NameComClient:
    name_factory = NameFactory()

    def __init__(self, domain, options):
        self.domain = domain.strip()
        options = options.get("namecom", {})

        if "username" not in options or "token" not in options:
            raise DnsConfigError("username and token need to be configured for name.com dns client")

        self.username = options["username"]
        self.token = options["token"]
        self.debug = options.get("debug", False)

        self.client = self.name_factory.get(self.username, self.token, self.debug)

    def create_cname_record(self, subdomain, prefix, points_to):
        subdomain = f"{subdomain}.{prefix}"
        resp = self.client.create_record(self.domain, subdomain, "cname", points_to)
        return resp["id"]

    def delete_cname_record(self, subdomain, prefix):
        subdomain = f"{subdomain}.{prefix}"
        for record in self.client.list_records(self.domain, subdomain):
            self.client.delete_record(record["fqdn"][:-1], record["id"])
