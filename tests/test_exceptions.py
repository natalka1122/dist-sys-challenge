"""Tests for custom exceptions."""

from exceptions import BadMessageError


class TestBadMessageError:
    def test_is_exception_subclass(self) -> None:
        assert issubclass(BadMessageError, Exception)
