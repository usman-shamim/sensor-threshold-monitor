"""Tests for the emergency shutdown controller (outcome mapping + latch)."""

from sentinelgui.shutdown_controller import ShutdownController


class FakeSerialAcked:
    def send_command(self, cmd):
        self.sent = cmd
        return True

    def read_ack(self, timeout_s=1.0):
        return "ACK:STOP"


class FakeSerialNoAck:
    def send_command(self, cmd):
        return True

    def read_ack(self, timeout_s=1.0):
        return None


class FakeSerialWriteFails:
    def send_command(self, cmd):
        raise IOError("port closed")


def test_trigger_latches_ui_safe_state_first():
    ctrl = ShutdownController(source=None)
    assert ctrl.is_latched is False
    event = ctrl.trigger(now="t")
    assert ctrl.is_latched is True
    assert event.ui_safe_state is True


def test_outcome_no_channel_on_simulator():
    event = ShutdownController(source=None).trigger(now="t")
    assert event.hardware_outcome == "no_channel"
    assert event.hardware_attempted is False


def test_outcome_acked_when_ack_received():
    event = ShutdownController(source=FakeSerialAcked()).trigger(now="t")
    assert event.hardware_outcome == "acked"
    assert event.hardware_attempted is True


def test_outcome_sent_when_no_ack():
    event = ShutdownController(source=FakeSerialNoAck()).trigger(now="t")
    assert event.hardware_outcome == "sent"


def test_outcome_failed_when_write_raises():
    event = ShutdownController(source=FakeSerialWriteFails()).trigger(now="t")
    assert event.hardware_outcome == "failed"
    assert event.hardware_attempted is True


def test_resume_clears_latch():
    ctrl = ShutdownController(source=None)
    ctrl.trigger(now="t")
    ctrl.resume()
    assert ctrl.is_latched is False
