from enum import Enum
from typing import List

from .coredns import CoreDNS
from .name import NameComClient
from .exceptions import DnsConfigError, DomainConfigError, PrefixIsNotAllowed

class ClientType(Enum):
    COREDNS = "coredns"
    NAMECOM = "namecom"


CLIENTS = {
    ClientType.COREDNS: CoreDNS,
    ClientType.NAMECOM: NameComClient,
}


class Domain:

    def __init__(self, name, allowed_prefixes):
        self.name = name
        self.allowed_prefixes = allowed_prefixes

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return other.name == self.name

    def __hash__(self):
        return hash(self.name)

    __repr__ = __str__


class Client:

    def __init__(self, client_type, domains: List[Domain], options):
        self.client_type = client_type
        self.domains = domains

        self.domain_clients = {}
        for domain in self.domains:
            self.domain_clients[domain] = CLIENTS[client_type](domain.name, options)

        self.options = options

    def verify(self, host):
        for domain in self.domains:
            name = domain.name

            if host.endswith(f".{name}"):
                subdomain_with_prefix = host.replace(f".{name}", "")
                try:
                    subdomain, prefix = subdomain_with_prefix.split(".", 1)
                except ValueError:
                    # no prefix is provided
                    subdomain, prefix = subdomain_with_prefix, ""

                if prefix not in domain.allowed_prefixes:
                    raise PrefixIsNotAllowed(f"'{prefix}' prefix is not allowed in '{name}' configuration")
                return subdomain, prefix, domain

        raise DomainConfigError(f"main/parent domain of '{host}' is not configured")

    def select(self, host):
       subdomain, prefix, domain = self.verify(host)
       return subdomain, prefix, self.domain_clients[domain]

    def create_cname_record(self, host, points_to):
        subdomain, prefix, client = self.select(host)
        return client.create_cname_record(subdomain, prefix, points_to)

    def delete_cname_record(self, host):
        subdomain, prefix, client = self.select(host)
        return client.delete_cname_record(subdomain, prefix)
