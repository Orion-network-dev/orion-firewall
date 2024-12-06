import unittest
from orion_config import FirewallConfig
from marshmallow.exceptions import ValidationError

class TestStringMethods(unittest.TestCase):

    def test_deserialize_config_single_port(self):
        CONFIG = {
            "overrideMemberId": None,
            "expose": [
                {
                    "protocol": "udp",
                    "port": 123,
                    "address": "10.30.1.1",
                    "redirectPort": 123,
                    "masquerade": True,
                }
            ],
        }
        
        configSchema = FirewallConfig()
        configSchema.load(CONFIG)
    def test_deserialize_config_multiple_port(self):
        CONFIG = {
            "overrideMemberId": None,
            "expose": [
                {
                    "protocol": "udp",
                    "port": [123, 456],
                    "address": "10.30.1.1",
                    "redirectPort": [123, 456],
                    "masquerade": True,
                }
            ],
        }
        
        configSchema = FirewallConfig()
        configSchema.load(CONFIG)
    def test_deserialize_different_ports_datatype(self):
        CONFIG = {
            "overrideMemberId": None,
            "expose": [
                {
                    "protocol": "udp",
                    "port": 123,
                    "address": "10.30.1.1",
                    "redirectPort": [123],
                    "masquerade": True,
                }
            ],
        }
        
        configSchema = FirewallConfig()
        # ensure that a validation error is raised
        self.assertRaises(ValidationError, lambda: configSchema.load(CONFIG))
    def test_deserialize_wrong_protocol_ports(self):
        CONFIG = {
            "overrideMemberId": None,
            "expose": [
                {
                    "protocol": "icmp",
                    "port": 123,
                    "address": "10.30.1.1",
                    "redirectPort": 123,
                    "masquerade": True,
                }
            ],
        }
        
        configSchema = FirewallConfig()
        self.assertRaises(ValidationError, lambda: configSchema.load(CONFIG))
    def test_deserialize_wrong_protocol_not_ports(self):
        CONFIG = {
            "overrideMemberId": None,
            "expose": [
                {
                    "protocol": "tcp",
                    "address": "10.30.1.1",
                    "masquerade": True,
                }
            ],
        }
        
        configSchema = FirewallConfig()
        self.assertRaises(ValidationError, lambda: configSchema.load(CONFIG))
