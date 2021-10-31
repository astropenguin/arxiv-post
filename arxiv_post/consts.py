__all__ = [
    "CATEGORIES",
    "KEYWORDS",
    "START_DATE",
    "END_DATE",
    "SOURCE_LANG",
    "TARGET_LANG",
    "DEEPL_MODE",
    "N_CONCURRENT",
    "TIMEOUT",
    "DeepLMode",
]


# standard library
from typing import Literal


# constants
CATEGORIES = ("astro-ph.*",)
KEYWORDS = ()
START_DATE = "3 days ago at midnight in UTC"
END_DATE = "2 days ago at midnight in UTC"
SOURCE_LANG = "en"
TARGET_LANG = "ja"
DEEPL_MODE = "auto"
N_CONCURRENT = 2
TIMEOUT = 30.0


# type hints
DeepLMode = Literal["auto", "api", "browser"]
