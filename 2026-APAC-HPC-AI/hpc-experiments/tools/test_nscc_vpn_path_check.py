"""Regression: namespace readiness must not be mistaken for VPN access."""
import json
import subprocess
import unittest
from unittest.mock import patch, MagicMock
import nscc_vpn_path_check as probe


class PathHealthTests(unittest.TestCase):
    def body(self, addresses, banner=None, unreachable=False):
        ip_result = subprocess.CompletedProcess([], 0, json.dumps(addresses))
        peer = MagicMock()
        peer.__enter__.return_value.recv.return_value = banner
        with patch('subprocess.run', return_value=ip_result), patch('socket.create_connection') as connect:
            if unreachable:
                connect.side_effect = OSError('unreachable fixture')
            else:
                connect.return_value = peer
            scope = {}
            with patch('builtins.print'):
                exec(probe.BODY, scope)
            return scope['result'], connect.called

    def test_namespace_without_tunnel_never_opens_ssh(self):
        result, called = self.body([])
        self.assertEqual(result['state'], 'TUNNEL_NOT_READY')
        self.assertFalse(called)

    def test_tunnel_without_address_never_opens_ssh(self):
        result, called = self.body([{'flags': ['UP'], 'addr_info': []}])
        self.assertEqual(result['state'], 'TUNNEL_NOT_READY')
        self.assertFalse(called)

    def test_tunnel_without_reachable_service_is_not_access(self):
        result, _ = self.body([{'flags': ['UP'], 'addr_info': [{'family': 'inet'}]}], unreachable=True)
        self.assertEqual(result['state'], 'TUNNEL_PRESENT_SSH_UNREACHABLE')

    def test_non_ssh_banner_is_not_ssh_access(self):
        result, _ = self.body([{'flags': ['UP'], 'addr_info': [{'family': 'inet'}]}], b'HTTP/1.1')
        self.assertEqual(result['state'], 'TUNNEL_PRESENT_SSH_UNREACHABLE')

    def test_ssh_banner_still_does_not_prove_authentication(self):
        result, _ = self.body([{'flags': ['UP'], 'addr_info': [{'family': 'inet'}]}], b'SSH-2.0-fixture')
        self.assertEqual(result['state'], 'SSH_SERVICE_REACHABLE_AUTH_UNTESTED')
        self.assertFalse(result['ssh_authentication_tested'])

    def test_absent_namespace_remains_unavailable(self):
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 1, '', 'private fixture')):
            result = probe.check()
        self.assertEqual(result['state'], 'NAMESPACE_UNAVAILABLE')
        self.assertNotIn('private fixture', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
