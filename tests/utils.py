FIXED_TS = "2025-07-06T12:00:00+00:00"


class DummyDateTime:
    @classmethod
    def now(cls, tz=None):
        return cls()

    def isoformat(self):
        return FIXED_TS
