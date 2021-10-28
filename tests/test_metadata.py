# dependencies
import astro_ph


# constants
AUTHOR = "Akio Taniguchi"
VERSION = "0.3.0"


# test functions
def test_author() -> None:
    assert astro_ph.__author__ == AUTHOR


def test_version() -> None:
    assert astro_ph.__version__ == VERSION
