from proman.dependencies import __version__


def test_version() -> None:
    assert __version__ == '0.1.1-dev3'
