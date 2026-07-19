#!/usr/bin/env python3
"""
Vemex USSD Auth Layer Tests
============================
Tests for authenticated USSD/balance checks.
"""

import json
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))
from vemex_ussd_auth_layer import USSDAuthLayer, AuthState
from vemex_sim_automation import VemexSIMAutomation, USSDSession


class TestAuthState(unittest.TestCase):
    def test_initial_state(self):
        state = AuthState(device_serial="test")
        self.assertFalse(state.authenticated)
        self.assertIsNone(state.session_token)
        self.assertIsNone(state.expected_balance)
        self.assertFalse(state.matched)

    def test_session_validity(self):
        state = AuthState(device_serial="test", authenticated=True)
        state.last_auth_time = time.time()
        self.assertTrue(state.last_auth_time is not None and (time.time() - state.last_auth_time) < 300)
        state.last_auth_time = time.time() - 1000
        self.assertFalse(state.last_auth_time is not None and (time.time() - state.last_auth_time) < 300)


class TestUSSDAuthLayer(unittest.TestCase):
    def setUp(self):
        self.sim = VemexSIMAutomation(device_serial="1bbfce51")
        self.auth = USSDAuthLayer(device_serial="1bbfce51", sim_automation=self.sim)

    def test_initial_auth_state(self):
        state = self.auth.get_auth_state()
        self.assertFalse(state["authenticated"])
        self.assertIsNone(state["session_token"])

    @patch("subprocess.run")
    def test_authenticate_portal_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )
        self.auth._adb = lambda cmd, timeout=20: "agp-redirect-id=test-session-123; Path=/; Secure; HttpOnly"
        result = self.auth.authenticate_portal()
        self.assertTrue(result["success"])
        self.assertTrue(result["authenticated"])
        self.assertEqual(result["session_token"], "test-session-123")
        self.assertEqual(self.auth.auth_state.session_token, "test-session-123")

    @patch("subprocess.run")
    def test_authenticate_portal_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        result = self.auth.authenticate_portal()
        self.assertFalse(result["success"])
        self.assertFalse(result["authenticated"])
        self.assertIsNotNone(result["error"])

    def test_ensure_authenticated_creates_session(self):
        with patch.object(self.auth, "authenticate_portal") as mock_auth:
            mock_auth.return_value = {"success": True, "authenticated": True, "session_token": "abc123"}
            result = self.auth.ensure_authenticated()
            self.assertTrue(result)
            self.assertEqual(self.auth.auth_state.session_token, "abc123")

    def test_ensure_authenticated_reuses_valid_session(self):
        self.auth.auth_state.authenticated = True
        self.auth.auth_state.last_auth_time = time.time()
        with patch.object(self.auth, "authenticate_portal") as mock_auth:
            result = self.auth.ensure_authenticated()
            self.assertTrue(result)
            mock_auth.assert_not_called()

    @patch.object(USSDAuthLayer, "ensure_authenticated")
    @patch.object(VemexSIMAutomation, "send_ussd")
    def test_send_authenticated_ussd(self, mock_send_ussd, mock_auth):
        mock_auth.return_value = True
        mock_send_ussd.return_value = USSDSession(
            code="*122#",
            raw_response="Tu saldo es 197.94 DOP",
            balance="197.94",
            currency="DOP",
            parsed=True,
        )
        result = self.auth.send_authenticated_ussd("*122#")
        self.assertTrue(result["success"])
        self.assertEqual(result["balance"], "197.94")
        self.assertEqual(result["currency"], "DOP")

    @patch.object(USSDAuthLayer, "ensure_authenticated")
    def test_send_authenticated_ussd_auth_failure(self, mock_auth):
        mock_auth.return_value = False
        result = self.auth.send_authenticated_ussd("*122#")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "auth_failed")

    def test_verify_balance_match_success(self):
        result = self.auth.verify_balance_match("197.94", "197.94")
        self.assertTrue(result["matched"])
        self.assertEqual(result["delta"], 0.0)

    def test_verify_balance_match_small_delta(self):
        result = self.auth.verify_balance_match("197.94", "197.95")
        self.assertFalse(result["matched"])
        self.assertEqual(result["delta"], 0.01)

    def test_verify_balance_match_no_actual(self):
        result = self.auth.verify_balance_match("197.94", None)
        self.assertFalse(result["matched"])
        self.assertIn("no_actual_balance", result["error"])

    def test_verify_balance_match_invalid_actual(self):
        result = self.auth.verify_balance_match("197.94", "abc")
        self.assertFalse(result["matched"])
        self.assertIn("parse_error", result["error"])

    def test_run_authenticated_balance_check(self):
        with patch.object(self.auth, "ensure_authenticated") as mock_auth:
            mock_auth.return_value = True
            with patch.object(self.sim, "send_ussd") as mock_send_ussd:
                mock_send_ussd.return_value = USSDSession(
                    code="*122#",
                    raw_response="Tu saldo es 197.94 DOP",
                    balance="197.94",
                    currency="DOP",
                    parsed=True,
                )
                self.auth.auth_state.expected_balance = "197.94"
                self.auth.auth_state.authenticated = True
                self.auth.auth_state.last_auth_time = time.time()
                result = self.auth.run_authenticated_balance_check("interface_1")
                self.assertTrue(result["success"])
                self.assertTrue(result["match"]["matched"])
                self.assertTrue(result["auth"]["authenticated"])

    @patch.object(USSDAuthLayer, "ensure_authenticated")
    def test_run_authenticated_balance_check_auth_failure(self, mock_auth):
        mock_auth.return_value = False
        result = self.auth.run_authenticated_balance_check("interface_1")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "auth_failed")

    def test_max_auth_attempts(self):
        self.auth.auth_state.auth_attempts = 3
        result = self.auth.authenticate_portal()
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "max_auth_attempts_reached")


class TestAuthLayerIntegration(unittest.TestCase):
    def test_full_auth_and_balance_flow(self):
        sim = VemexSIMAutomation(device_serial="test")
        auth = USSDAuthLayer(device_serial="test", sim_automation=sim)

        with patch.object(auth, "authenticate_portal") as mock_auth:
            mock_auth.return_value = {
                "success": True,
                "authenticated": True,
                "session_token": "session-123",
                "cookie_token": "agp-redirect-id=session-123",
            }
            with patch.object(sim, "send_ussd") as mock_ussd:
                mock_ussd.return_value = USSDSession(
                    code="*122#",
                    raw_response="Tu saldo es 197.94 DOP",
                    balance="197.94",
                    currency="DOP",
                    parsed=True,
                )
                auth.auth_state.expected_balance = "197.94"
                result = auth.run_authenticated_balance_check("interface_1")
                self.assertTrue(result["success"])
                self.assertTrue(result["match"]["matched"])
                self.assertEqual(result["auth"]["session_token"], "session-123")


if __name__ == "__main__":
    unittest.main()
