__all__ = [
    "CATEGORIES",
    "KEYWORDS",
    "START_DATE",
    "END_DATE",
    "LANGUAGE_FROM",
    "LANGUAGE_TO",
    "N_CONCURRENT",
    "TIMEOUT",
    "Language",
]


# standard library
from enum import auto, Enum


# constants
CATEGORIES = ("astro-ph.*",)
KEYWORDS = ()
START_DATE = "3 days ago at midnight in UTC"
END_DATE = "2 days ago at midnight in UTC"
LANGUAGE_FROM = "en"
LANGUAGE_TO = "auto"
N_CONCURRENT = 10
TIMEOUT = 30.0


class Language(Enum):
    """Available languages in the package."""

    AUTO = auto()  #: Auto language detection
    BG = auto()  #: Bulgarian
    CS = auto()  #: Czech
    DA = auto()  #: Danish
    DE = auto()  #: German
    EL = auto()  #: Greek
    EN = auto()  #: English
    ES = auto()  #: Spanish
    ET = auto()  #: Estonian
    FI = auto()  #: Finnish
    FR = auto()  #: French
    HU = auto()  #: Hungarian
    IT = auto()  #: Italian
    JA = auto()  #: Japanese
    LT = auto()  #: Lithuanian
    LV = auto()  #: Latvian
    NL = auto()  #: Dutch
    PL = auto()  #: Polish
    PT = auto()  #: Portuguese
    RO = auto()  #: Romanian
    RU = auto()  #: Russian
    SK = auto()  #: Slovak
    SL = auto()  #: Slovenian
    SV = auto()  #: Swedish
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
