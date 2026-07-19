#!/usr/bin/env python3
"""
Vemex Permanent Balance Token Tests
====================================
Tests for permanent non-expendable balance token storage.
"""

import json
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))
from vemex_permanent_balance_token import PermanentBalanceToken, BalanceToken
from vemex_ussd_auth_layer import USSDAuthLayer
from vemex_sim_automation import VemexSIMAutomation


class TestBalanceToken(unittest.TestCase):
    def test_token_creation(self):
        token = BalanceToken(token_id="t1", balance="197.94", currency="DOP", interface="interface_1")
        self.assertEqual(token.balance, "197.94")
        self.assertFalse(token.is_expired())

    def test_token_expiry(self):
        token = BalanceToken(token_id="t2", balance="10.00", currency="DOP", interface="interface_1", expires_at=time.time() - 100)
        self.assertTrue(token.is_expired())

    def test_token_serialization(self):
        token = BalanceToken(token_id="t3", balance="50.00", currency="USD", interface="interface_2")
        data = token.to_dict()
        restored = BalanceToken.from_dict(data)
        self.assertEqual(restored.balance, "50.00")
        self.assertEqual(restored.currency, "USD")


class TestPermanentBalanceToken(unittest.TestCase):
    def setUp(self):
        self.sim = VemexSIMAutomation(device_serial="1bbfce51")
        self.auth = USSDAuthLayer(device_serial="1bbfce51", sim_automation=self.sim)
        self.token_mgr = PermanentBalanceToken(device_serial="1bbfce51", auth_layer=self.auth)
        self._clean_token_store()

    def _clean_token_store(self):
        try:
            subprocess.run(
                ["adb", "-s", "1bbfce51", "shell", "rm", "-f", "/data/local/tmp/vemex_balance_tokens.json"],
                capture_output=True, text=True, timeout=10,
            )
        except Exception:
            pass
        self.token_mgr.tokens = []

    def test_initial_status_empty(self):
        status = self.token_mgr.get_status()
        self.assertEqual(status["total_tokens"], 0)
        self.assertEqual(status["latest_balance"], None)

    @patch.object(USSDAuthLayer, "run_authenticated_balance_check")
    def test_create_token(self, mock_balance):
        self._clean_token_store()
        mock_balance.return_value = {
            "success": True,
            "ussd_result": {"balance": "197.94", "currency": "DOP", "parsed": True},
            "match": {"matched": True},
        }
        result = self.token_mgr.refresh_from_ussd("interface_1")
        self.assertTrue(result["success"])
        self.assertEqual(result["action"], "created")
        self.assertEqual(result["balance"], "197.94")
        self.assertIsNotNone(result.get("token_id"))

    @patch.object(USSDAuthLayer, "run_authenticated_balance_check")
    def test_update_to_higher_value(self, mock_balance):
        self._clean_token_store()
        mock_balance.return_value = {
            "success": True,
            "ussd_result": {"balance": "197.94", "currency": "DOP", "parsed": True},
            "match": {"matched": True},
        }
        r1 = self.token_mgr.refresh_from_ussd("interface_1")
        self.assertEqual(r1["balance"], "197.94")
        self.assertEqual(r1["action"], "created")

        mock_balance.return_value = {
            "success": True,
            "ussd_result": {"balance": "249.50", "currency": "DOP", "parsed": True},
            "match": {"matched": False},
        }
        r2 = self.token_mgr.refresh_from_ussd("interface_1")
        self.assertEqual(r2["balance"], "249.50")
        self.assertEqual(r2["action"], "updated")
        self.assertEqual(r2["token_id"], r1["token_id"])

    @patch.object(USSDAuthLayer, "run_authenticated_balance_check")
    def test_origin_layer_returns_highest_updated_value(self, mock_balance):
        self._clean_token_store()
        mock_balance.return_value = {
            "success": True,
            "ussd_result": {"balance": "100.00", "currency": "DOP", "parsed": True},
            "match": {"matched": True},
        }
        self.token_mgr.refresh_from_ussd("interface_1")

        mock_balance.return_value = {
            "success": True,
            "ussd_result": {"balance": "250.00", "currency": "DOP", "parsed": True},
            "match": {"matched": False},
        }
        self.token_mgr.refresh_from_ussd("interface_1")

        origin = self.token_mgr.get_origin_layer_value()
        self.assertTrue(origin["success"])
        self.assertEqual(origin["origin_balance"], "250.00")

    @patch.object(USSDAuthLayer, "run_authenticated_balance_check")
    def test_multiple_interfaces(self, mock_balance):
        self._clean_token_store()
        mock_balance.return_value = {
            "success": True,
            "ussd_result": {"balance": "197.94", "currency": "DOP", "parsed": True},
            "match": {"matched": True},
        }
        self.token_mgr.refresh_from_ussd("interface_1")

        mock_balance.return_value = {
            "success": True,
            "ussd_result": {"balance": "85.20", "currency": "DOP", "parsed": True},
            "match": {"matched": True},
        }
        self.token_mgr.refresh_from_ussd("interface_2")

        latest = self.token_mgr.get_latest_token()
        self.assertIsNotNone(latest)
        self.assertIn(latest.interface, ["interface_1", "interface_2"])

        status = self.token_mgr.get_status()
        self.assertEqual(status["total_tokens"], 2)

    @patch.object(USSDAuthLayer, "run_authenticated_balance_check")
    def test_cross_interface_sync_detects_divergence(self, mock_balance):
        self._clean_token_store()
        mock_balance.return_value = {
            "success": True,
            "ussd_result": {"balance": "197.94", "currency": "DOP", "parsed": True},
            "match": {"matched": True},
        }
        r1 = self.token_mgr.refresh_from_ussd("interface_1")

        mock_balance.return_value = {
            "success": True,
            "ussd_result": {"balance": "0.00", "currency": "DOP", "parsed": True},
            "match": {"matched": False},
        }
        r2 = self.token_mgr.refresh_from_ussd("interface_2")

        self.assertEqual(r1["balance"], "197.94")
        self.assertEqual(r2["balance"], "0.00")
        self.assertIn("cross_interface_sync", r2)
        self.assertFalse(r2["cross_interface_sync"]["synchronized"])
        self.assertEqual(abs(r2["cross_interface_sync"]["delta"]), 197.94)

    def test_no_tokens_origin_layer(self):
        self._clean_token_store()
        origin = self.token_mgr.get_origin_layer_value()
        self.assertFalse(origin["success"])
        self.assertEqual(origin["error"], "no_tokens")


if __name__ == "__main__":
    unittest.main()
