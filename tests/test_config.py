import os
from unittest import TestCase

from acme.helper import load_config
from zerossl_ca_handler import CAhandler, get_domain_config, get_dns_options


CURRENT_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(os.path.dirname(CURRENT_DIR), "config/acme_srv.zerossl.cfg")


class TestConfig(TestCase):
    def setUp(self):
        self.config = load_config(cfg_file=CONFIG_PATH)

    def test_load_domain_config(self):
        domains = get_domain_config(self.config)
        self.assertEqual(len(domains), 2)

    def test_load_dns_client_config(self):
        dns_options = get_dns_options(self.config)
        self.assertIn("namecom", dns_options)
