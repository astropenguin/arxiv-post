# third-party packages
import chromedriver_binary  # noqa
from astro_ph.deepl import Language, translate
from typing_extensions import Final


# constants
TEXT_EN: Final[str] = "This is a test script."
TEXT_JA: Final[str] = "これはテストスクリプトです。"


# main features
def test_translate():
    assert translate(TEXT_EN, Language.JA) == TEXT_JA
