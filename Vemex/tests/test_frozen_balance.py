#!/usr/bin/env python3
"""
Vemex Frozen Balance Mode Tests
================================
Tests for frozen balance mode with telephony hooks.
"""

import json
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))
from vemex_frozen_balance import VemexFrozenBalance, FrozenBalanceState
from vemex_ussd_auth_layer import USSDAuthLayer
from vemex_sim_automation import VemexSIMAutomation, USSDSession


class TestFrozenBalanceState(unittest.TestCase):
    def test_initial_state(self):
        state = FrozenBalanceState()
        self.assertFalse(state.enabled)
        self.assertIsNone(state.frozen_balance)
        self.assertIsNone(state.frozen_at)

    def test_enabled_state(self):
        state = FrozenBalanceState(enabled=True, frozen_balance="197.94", frozen_at=time.time())
        self.assertTrue(state.enabled)
        self.assertEqual(state.frozen_balance, "197.94")


class TestVemexFrozenBalance(unittest.TestCase):
    def setUp(self):
        self.sim = VemexSIMAutomation(device_serial="1bbfce51")
        self.auth = USSDAuthLayer(device_serial="1bbfce51", sim_automation=self.sim)
        self.frozen = VemexFrozenBalance(device_serial="1bbfce51", auth_layer=self.auth)
        self._clean_frozen_state()

    def _clean_frozen_state(self):
        try:
            subprocess.run(
                ["adb", "-s", "1bbfce51", "shell", "rm", "-f", "/data/local/tmp/vemex_frozen_balance.json"],
                capture_output=True, text=True, timeout=10,
            )
        except Exception:
            pass
        self.frozen.state = FrozenBalanceState()

    def test_initial_status(self):
        status = self.frozen.get_status()
        self.assertFalse(status["frozen_enabled"])
        self.assertIsNone(status["frozen_balance"])
        self.assertFalse(status["telephony_hook_active"])

    def test_enable_frozen_mode(self):
        with patch.object(self.frozen, "_install_telephony_hook") as mock_hook:
            mock_hook.return_value = True
            result = self.frozen.enable_frozen_mode("197.94", "DOP", "interface_1")
            self.assertTrue(result["success"])
            self.assertEqual(result["frozen_balance"], "197.94")
            self.assertEqual(result["frozen_currency"], "DOP")
            self.assertTrue(result["telephony_hook_active"])

    def test_disable_frozen_mode(self):
        with patch.object(self.frozen, "_uninstall_telephony_hook") as mock_hook:
            mock_hook.return_value = True
            self.frozen.enable_frozen_mode("197.94", "DOP", "interface_1")
            result = self.frozen.disable_frozen_mode()
            self.assertTrue(result["success"])
            self.assertFalse(self.frozen.state.enabled)

    def test_frozen_ussd_response(self):
        self.frozen.enable_frozen_mode("197.94", "DOP", "interface_1")
        result = self.frozen.get_frozen_ussd_response("*122#")
        self.assertTrue(result["frozen"])
        self.assertEqual(result["balance"], "197.94")
        self.assertEqual(result["currency"], "DOP")
        self.assertIn("197.94", result["raw_response"])

    def test_frozen_mode_ignores_live_divergence(self):
        with patch.object(self.frozen, "_install_telephony_hook") as mock_hook:
            mock_hook.return_value = True
            self.frozen.enable_frozen_mode("197.94", "DOP", "interface_1")
        
        with patch.object(self.frozen, "get_frozen_ussd_response") as mock_frozen:
            mock_frozen.return_value = {
                "frozen": True,
                "code": "*122#",
                "balance": "197.94",
                "currency": "DOP",
                "raw_response": "Tu saldo es 197.94 DOP",
                "parsed": True,
            }
            result = self.frozen.check_frozen_balance("interface_1")
            self.assertTrue(result["frozen"])
            self.assertEqual(result["frozen_balance"], "197.94")
            self.assertTrue(result["success"])

    def test_update_frozen_balance(self):
        with patch.object(self.frozen, "_install_telephony_hook") as mock_hook:
            mock_hook.return_value = True
            self.frozen.enable_frozen_mode("197.94", "DOP", "interface_1")
            result = self.frozen.update_frozen_balance("249.50", "DOP")
            self.assertTrue(result["success"])
            self.assertEqual(result["new_balance"], "249.50")
            self.assertEqual(self.frozen.state.frozen_balance, "249.50")

    def test_compare_with_live_detects_divergence(self):
        with patch.object(self.frozen, "send_frozen_ussd") as mock_ussd:
            mock_ussd.return_value = {
                "frozen": True,
                "code": "*122#",
                "balance": "0.00",
                "currency": "DOP",
                "raw_response": "Tu saldo es 0.00 DOP",
                "parsed": True,
            }
            self.frozen.enable_frozen_mode("197.94", "DOP", "interface_1")
            result = self.frozen.compare_with_live("interface_1")
            self.assertTrue(result["frozen"])
            self.assertTrue(result["diverged"])
            self.assertEqual(result["delta"], 197.94)
            self.assertEqual(self.frozen.state.divergence_count, 1)

    def test_compare_with_live_no_divergence(self):
        with patch.object(self.frozen, "send_frozen_ussd") as mock_ussd:
            mock_ussd.return_value = {
                "frozen": True,
                "code": "*122#",
                "balance": "197.94",
                "currency": "DOP",
                "raw_response": "Tu saldo es 197.94 DOP",
                "parsed": True,
            }
            self.frozen.enable_frozen_mode("197.94", "DOP", "interface_1")
            result = self.frozen.compare_with_live("interface_1")
            self.assertFalse(result["diverged"])
            self.assertEqual(result["delta"], 0.0)

    def test_frozen_mode_status_fields(self):
        with patch.object(self.frozen, "_install_telephony_hook") as mock_hook:
            mock_hook.return_value = True
            self.frozen.enable_frozen_mode("197.94", "DOP", "interface_1")
            status = self.frozen.get_status()
            self.assertTrue(status["frozen_enabled"])
            self.assertEqual(status["frozen_balance"], "197.94")
            self.assertTrue(status["telephony_hook_active"])
            self.assertEqual(status["override_source"], "manual")


if __name__ == "__main__":
    unittest.main()
