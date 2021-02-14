# third-party packages
from astro_ph.translate import Language, translate
from typing_extensions import Final


# constants
TEXT_EN: Final[str] = "This is a test script."
TEXT_JA: Final[str] = "これはテストスクリプトです。"


# test functions
def test_translate() -> None:
    assert translate(TEXT_EN, Language.JA) == TEXT_JA
