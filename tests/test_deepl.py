# third-party packages
from astro_ph.deepl import Driver, Language, translate
from typing_extensions import Final


# constants
TEXT_EN: Final[str] = "This is a test script."
TEXT_JA: Final[str] = "これはテストスクリプトです。"


# main features
def test_translate():
    text_ja = translate(TEXT_EN, Language.JA, driver=Driver.CHROME_REMOTE)
    assert text_ja == TEXT_JA
