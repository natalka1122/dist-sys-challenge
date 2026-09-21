"""Tests for the constant enums (MessageType, ErrorType)."""

from const import ErrorType, MessageType


class TestMessageType:
    def test_echo_value(self) -> None:
        assert MessageType.ECHO.value == "echo"

    def test_echo_ok_value(self) -> None:
        assert MessageType.ECHO_OK.value == "echo_ok"

    def test_init_value(self) -> None:
        assert MessageType.INIT.value == "init"

    def test_init_ok_value(self) -> None:
        assert MessageType.INIT_OK.value == "init_ok"

    def test_error_value(self) -> None:
        assert MessageType.ERROR.value == "error"


class TestErrorType:
    def test_not_supported_value(self) -> None:
        assert ErrorType.NOT_SUPPORTED.value == 10

    def test_crash_value(self) -> None:
        assert ErrorType.CRASH.value == 13
