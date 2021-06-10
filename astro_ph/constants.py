from enum import auto, Enum
from typing import Final


START_DATE: Final[str] = "3 days ago at midnight in UTC"
END_DATE: Final[str] = "2 days ago at midnight in UTC"
N_CONCURRENT: Final[int] = 10
TIMEOUT: Final[float] = 30.0


class Language(Enum):
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
