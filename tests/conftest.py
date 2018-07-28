import shutil

import pytest


@pytest.fixture
def clean_tmp():
    shutil.rmtree('tmp', ignore_errors=True)
