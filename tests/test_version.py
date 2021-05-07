# type: ignore
from proman_packaging import __version__


def test_version():
    assert __version__ == "0.1.1-dev1"
