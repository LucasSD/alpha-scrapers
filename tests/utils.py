"""
tests.utils module
==================

Test utilities and fixtures for the alpha_scrapers test suite.

Provides:
- FIXED_TS: a fixed timestamp string for deterministic tests
- DummyDateTime: a class to monkeypatch datetime for reproducible timestamps
"""

FIXED_TS = "2025-07-06T12:00:00+00:00"


class DummyDateTime:
    """
    Dummy datetime class for monkeypatching datetime in tests.

    The .now() method returns an instance whose .isoformat() returns FIXED_TS.
    """

    @classmethod
    def now(cls, tz=None):
        """
        Return a DummyDateTime instance (ignores tz argument).

        :param tz: Optional timezone argument (ignored)
        :type tz: Any
        :returns: DummyDateTime instance
        :rtype: DummyDateTime
        """
        return cls()

    def isoformat(self):
        """
        Return the fixed timestamp string for deterministic tests.

        :returns: Fixed timestamp string
        :rtype: str
        """
        return FIXED_TS
