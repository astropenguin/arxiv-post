__all__ = ["START_DATE", "END_DATE", "N_CONCURRENT", "TIMEOUT", "Language"]


# standard library
from enum import auto, Enum


# constants
START_DATE = "3 days ago at midnight in UTC"
END_DATE = "2 days ago at midnight in UTC"
N_CONCURRENT = 10
TIMEOUT = 30.0


class Language(Enum):
    """Available languages in the package."""

    AUTO = auto()  #: Auto language detection
    DE = auto()  #: German
    EN = auto()  #: English
    FR = auto()  #: French
    IT = auto()  #: Italian
    JA = auto()  #: Japanese
    ES = auto()  #: Spanish
    NL = auto()  #: Dutch
    PL = auto()  #: Polish
    PT = auto()  #: Portuguese
    RU = auto()  #: Russian
    ZH = auto()  #: Chinese

    @classmethod
    def from_str(cls, string: str) -> "Language":
        """Convert a string to a language."""
        return getattr(cls, string.upper())

    def to_str(self) -> str:
        """Convert a language to a string."""
        return self.name

    def __str__(self) -> str:
        return self.to_str()
