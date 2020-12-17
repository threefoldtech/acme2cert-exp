from unittest import TestCase
from dnsclient import Client, ClientType, Domain, DomainConfigError, PrefixIsNotAllowed



TEST_DOMAINS = [
    Domain("grid.tf", allowed_prefixes=["test", "test.devnet", "test.testnet"]),
    Domain("3bot.tf", allowed_prefixes=["test", "test.devnet", "test.testnet"])
]


TEST_OPTIONS_COREDNS = {"coredns": {}}
TEST_OPTIONS_NAMECOM = {"namecom": {"username": "test", "token": "test"}}
TEST_SUBDOMAINS = ["a", "b", "c"]

class DNSClientMixin:

    def test_register_domain(self):
        # test domain checking
        with self.assertRaises(DomainConfigError):
            self.client.create_cname_record("hello.test.mydom.tf", "dom1.com")

        with self.assertRaises(DomainConfigError):
            self.client.create_cname_record("grid.tf", "dom1.com")

        with self.assertRaises(DomainConfigError):
            self.client.create_cname_record("anothergrid.tf", "dom1.com")

        with self.assertRaises(DomainConfigError):
            self.client.create_cname_record("hello.test.mydom.tf", "dom1.com")

        with self.assertRaises(PrefixIsNotAllowed):
            self.client.create_cname_record("a.grid.tf", "dom1.com")

        for subdomain in TEST_SUBDOMAINS:
            for domain in TEST_DOMAINS:
                for prefix in domain.allowed_prefixes:
                    host = f"{subdomain}.{prefix}.{domain.name}"
                    self.client.create_cname_record(host, "dom1.com")

    def tearDown(self):
        for subdomain in TEST_SUBDOMAINS:
            for domain in TEST_DOMAINS:
                for prefix in domain.allowed_prefixes:
                    host = f"{subdomain}.{prefix}.{domain.name}"
                    self.client.delete_cname_record(host)

class TestCoreDNS(TestCase, DNSClientMixin):

    def setUp(self):
        self.client = Client(ClientType.COREDNS, domains=TEST_DOMAINS, options=TEST_OPTIONS_COREDNS)

class TestNameCom(TestCase, DNSClientMixin):
    def setUp(self):
        self.client = Client(ClientType.NAMECOM, domains=TEST_DOMAINS, options=TEST_OPTIONS_NAMECOM)

