from enum import Enum
from typing import List

from .name import NameComClient
from .exceptions import DomainConfigError, PrefixIsNotAllowed


class ClientType(Enum):
    NAMECOM = "namecom"


CLIENTS = {
    ClientType.NAMECOM: NameComClient,
}


class Domain:
    def __init__(self, name, allowed_prefixes, preferred_client_type=None):
        self.name = name
        self.allowed_prefixes = allowed_prefixes
        self.preferred_client_type = preferred_client_type

    def __str__(self):
        return f"{self.__class__.__name__}(name='{self.name}', allowed_prefixes={self.allowed_prefixes})"

    def __eq__(self, other):
        return other.name == self.name

    def __hash__(self):
        return hash(self.name)

    __repr__ = __str__


class Client:
    def __init__(self, client_types, domains: List[Domain], options):
        self.client_types = client_types
        self.domains = domains
        self.domain_clients = {}
        self.options = options

    def is_same_zone(self, subdomain, prefix):
        if not prefix:
            return True
        return subdomain == prefix or subdomain.endswith(prefix)

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

                if not any([self.is_same_zone(prefix, allowed_prefix) for allowed_prefix in domain.allowed_prefixes]):
                    raise PrefixIsNotAllowed(f"'{prefix}' prefix is not allowed in '{name}' configuration")
                return subdomain, prefix, domain

        raise DomainConfigError(f"main/parent domain of '{host}' is not configured")

    def select(self, host):
        subdomain, prefix, domain = self.verify(host)
        if domain in self.domain_clients:
            return subdomain, prefix, self.domain_clients[domain]

        if domain.preferred_client_type and domain.preferred_client_type.value in self.options:
            client_type = CLIENTS[domain.preferred_client_type]
        else:
            # get default (first) client type
            client_type = CLIENTS[self.client_types[0]]

        client = client_type(domain.name, self.options)
        self.domain_clients[domain] = client
        return subdomain, prefix, client

    def create_cname_record(self, host, points_to):
        subdomain, prefix, client = self.select(host)
        return client.create_cname_record(subdomain, prefix, points_to)

    def delete_cname_record(self, host):
        subdomain, prefix, client = self.select(host)
        return client.delete_cname_record(subdomain, prefix)
