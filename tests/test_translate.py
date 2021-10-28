# dependencies
from astro_ph.translate import Language, translate


# constants
TEXT_EN = "This is a test script."
TEXT_JA = "これはテストスクリプトです。"


# test functions
def test_translate() -> None:
    assert translate([TEXT_EN], Language.JA) == [TEXT_JA]
