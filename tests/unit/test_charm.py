# Copyright 2022 Jon Seager
# See LICENSE file for licensing details.

# This file contains basic tests simply to ensure that the various event handlers for operator
# framework are being called, and that they in turn are invoking the right helpers.
#
# The helpers themselves require too much mocking, and are validated in functional/integration
# tests.


import unittest
from subprocess import CalledProcessError
from unittest.mock import patch

import ops.testing
from ops.model import ActiveStatus, MaintenanceStatus
from ops.testing import Harness

from charm import JujuIntrospectCharm

ops.testing.SIMULATE_CAN_CONNECT = True


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(JujuIntrospectCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    @patch("charm.JujuIntrospect.install", lambda _: True)
    def test_install_success(self):
        self.harness.charm.on.install.emit()
        self.assertEqual(
            self.harness.charm.unit.status, MaintenanceStatus("installing juju-introspect")
        )

    @patch("charm.JujuIntrospectCharm._open_port")
    @patch("charm.JujuIntrospect.start")
    def test_start(self, ji_start, open_port):
        self.harness.charm.on.start.emit()
        ji_start.assert_called_once()
        open_port.assert_called_once()
        self.assertEqual(self.harness.charm.unit.status, ActiveStatus())

    @patch("charm.JujuIntrospect.remove")
    def test_remove(self, ji_stop):
        self.harness.charm.on.remove.emit()
        ji_stop.assert_called_once()
        self.assertEqual(
            self.harness.charm.unit.status, MaintenanceStatus("removing juju-introspect")
        )

    @patch("charm.check_call")
    def test_open_port(self, check_call):
        result = self.harness.charm._open_port()
        check_call.assert_called_with(["open-port", "6000/TCP"])
        self.assertTrue(result)

    @patch("charm.check_call")
    def test_open_port_fail(self, check_call):
        check_call.side_effect = CalledProcessError(1, "foo")
        result = self.harness.charm._open_port()
        check_call.assert_called_with(["open-port", "6000/TCP"])
        self.assertFalse(result)
