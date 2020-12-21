class DnsConfigError(Exception):
    pass


class DomainConfigError(DnsConfigError):
    pass


class PrefixIsNotAllowed(DomainConfigError):
    pass
