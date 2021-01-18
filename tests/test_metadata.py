import astro_ph


def test_author():
    assert astro_ph.__author__ == "Akio Taniguchi"


def test_version():
    assert astro_ph.__version__ == "0.1.0"
