#!/usr/bin/env python3
"""
Vemex SIM Automation Test Suite
================================
Backend and interface tests for SIM USSD/balance automation.
"""

import json
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))
from vemex_sim_automation import VemexSIMAutomation, USSDSession, SIMAccountState


class TestUSSDParsing(unittest.TestCase):
    def test_parse_balance_with_currency(self):
        sim = VemexSIMAutomation(device_serial="test")
        session = USSDSession(code="*122#", raw_response="Tu saldo es 197.94 DOP")
        parsed = sim._parse_ussd_response(session)
        self.assertEqual(parsed.balance, "197.94")
        self.assertEqual(parsed.currency, "DOP")
        self.assertTrue(parsed.parsed)

    def test_parse_balance_usd(self):
        sim = VemexSIMAutomation(device_serial="test")
        session = USSDSession(code="*112#", raw_response="Balance: 197.94 USD")
        parsed = sim._parse_ussd_response(session)
        self.assertEqual(parsed.balance, "197.94")
        self.assertEqual(parsed.currency, "USD")

    def test_parse_expiry(self):
        sim = VemexSIMAutomation(device_serial="test")
        session = USSDSession(code="*122#", raw_response="Saldo vence 12/31/2026")
        parsed = sim._parse_ussd_response(session)
        self.assertEqual(parsed.expiry, "12/31/2026")

    def test_parse_bonus(self):
        sim = VemexSIMAutomation(device_serial="test")
        session = USSDSession(code="*112#", raw_response="Bonus 5.25 disponible")
        parsed = sim._parse_ussd_response(session)
        self.assertEqual(parsed.bonus, "5.25")

    def test_parse_no_match(self):
        sim = VemexSIMAutomation(device_serial="test")
        session = USSDSession(code="*122#", raw_response="Servicio no disponible")
        parsed = sim._parse_ussd_response(session)
        self.assertFalse(parsed.parsed)
        self.assertIsNone(parsed.balance)


class TestSIMAutomationDataModel(unittest.TestCase):
    def test_ussd_session_defaults(self):
        session = USSDSession(code="*122#", raw_response="test")
        self.assertEqual(session.code, "*122#")
        self.assertFalse(session.parsed)
        self.assertIsNone(session.balance)

    def test_sim_account_state_defaults(self):
        account = SIMAccountState(serial="test", operator="TEST", mcc_mnc="123", sim_state="LOADED")
        self.assertFalse(account.data_registered)
        self.assertFalse(account.voice_registered)
        self.assertEqual(len(account.ussd_sessions), 0)


class TestBackendLogic(unittest.TestCase):
    def setUp(self):
        self.sim = VemexSIMAutomation(device_serial="1bbfce51")

    @patch("subprocess.run")
    def test_probe_telephony_parsing(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="mVoiceRegState=0(IN_SERVICE), mDataRegState=0(IN_SERVICE), mOperatorAlphaLong=CLARO DOM, mSimState=LOADED\n",
            returncode=0,
        )
        state = self.sim.probe_telephony()
        self.assertEqual(state["voice"], "0(IN_SERVICE)")
        self.assertEqual(state["data"], "0(IN_SERVICE)")
        self.assertEqual(state["operator"], "CLARO DOM")
        self.assertEqual(state["sim_state"], "LOADED")

    @patch("subprocess.run")
    def test_send_ussd_success(self, mock_run):
        mock_run.return_value = MagicMock(stdout="Parcel(00000000 00000001 'Tu saldo 197.94 DOP')", returncode=0)
        session = self.sim.send_ussd("*122#")
        self.assertEqual(session.code, "*122#")
        self.assertTrue(session.parsed)
        self.assertEqual(session.balance, "197.94")

    @patch("subprocess.run")
    def test_send_ussd_error(self, mock_run):
        mock_run.side_effect = Exception("timeout")
        session = self.sim.send_ussd("*122#")
        self.assertIn("ERROR", session.raw_response)
        self.assertFalse(session.parsed)

    def test_check_balance_interface_mapping(self):
        with patch.object(self.sim, "send_ussd") as mock_ussd:
            mock_ussd.return_value = USSDSession(code="*122#", raw_response="ok", balance="197.94", currency="DOP", parsed=True)
            result = self.sim.check_balance("interface_1")
            mock_ussd.assert_called_with("*122#")
            self.assertEqual(result["balance"], "197.94")

    def test_check_all_balances_delay(self):
        with patch.object(self.sim, "send_ussd") as mock_ussd:
            mock_ussd.return_value = USSDSession(code="*122#", raw_response="ok", parsed=True)
            start = time.time()
            self.sim.check_all_balances()
            elapsed = time.time() - start
            self.assertGreaterEqual(elapsed, 1.0)
            self.assertEqual(mock_ussd.call_count, 2)


class TestBackendTestSuite(unittest.TestCase):
    def setUp(self):
        self.sim = VemexSIMAutomation(device_serial="1bbfce51")

    @patch.object(VemexSIMAutomation, "_adb")
    def test_backend_tests_adb(self, mock_adb):
        mock_adb.return_value = "ok"
        result = self.sim.run_backend_tests()
        self.assertIn("tests", result)
        self.assertGreaterEqual(result["passed"], 1)

    @patch.object(VemexSIMAutomation, "probe_telephony")
    @patch.object(VemexSIMAutomation, "send_ussd")
    def test_backend_tests_telephony_and_ussd(self, mock_ussd, mock_probe):
        mock_probe.return_value = {
            "voice": "0(IN_SERVICE)",
            "data": "0(IN_SERVICE)",
            "operator": "CLARO DOM",
            "sim_state": "LOADED",
        }
        mock_ussd.return_value = USSDSession(code="*122#", raw_response="ok", parsed=True)
        result = self.sim.run_backend_tests()
        names = [t["name"] for t in result["tests"]]
        self.assertIn("ADB_AVAILABLE", names)
        self.assertIn("VOICE_REGISTERED", names)
        self.assertIn("DATA_REGISTERED", names)
        self.assertIn("OPERATOR_CLARO", names)
        self.assertIn("SIM_LOADED", names)
        self.assertIn("USSD_interface_1", names)
        self.assertIn("USSD_interface_2", names)


class TestInterfaceTestSuite(unittest.TestCase):
    def setUp(self):
        self.sim = VemexSIMAutomation(device_serial="1bbfce51")

    @patch.object(VemexSIMAutomation, "check_balance")
    @patch.object(VemexSIMAutomation, "get_account_state")
    def test_interface_tests_flow(self, mock_state, mock_balance):
        mock_balance.side_effect = [
            {"balance": "25.50", "currency": "DOP", "parsed": True, "raw_response": "ok"},
            {"balance": "10.00", "currency": "DOP", "parsed": True, "raw_response": "ok"},
        ]
        mock_state.return_value = {
            "operator": "CLARO DOM",
            "ussd_sessions": [{"code": "*122#"}, {"code": "*112#"}],
        }
        result = self.sim.run_interface_tests()
        names = [t["name"] for t in result["tests"]]
        self.assertIn("BALANCE_INTERFACE_1", names)
        self.assertIn("BALANCE_INTERFACE_2", names)
        self.assertIn("ACCOUNT_STATE", names)
        self.assertIn("OPERATOR_PRESENT", names)


if __name__ == "__main__":
    unittest.main()
