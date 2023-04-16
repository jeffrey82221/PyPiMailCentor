import os
import pytest
from src.update_latest import UpdateController

@pytest.fixture
def controller():
    if os.path.exists('tests/controller.csv'):
        os.remove('tests/controller.csv')
    if os.path.exists('tests/pandas.json'):
        os.remove('tests/pandas.json')
    return UpdateController('tests/controller.csv', 'tests')

def test_already_download(controller):
    assert not controller.already_download('pandas')
    controller.update_release_count('pandas', 1)
    assert controller.already_download('pandas')
    assert not controller.already_download('tensorflow')
    controller.update_release_count('tensorflow', 1)
    assert controller.already_download('tensorflow')
    controller.update_release_count('tensorflow', 2)
    assert controller.already_download('tensorflow')
    
def test_get_offline_release_count(controller):
    assert controller.get_offline_release_count('pandas') == 0
    controller.update_release_count('pandas', 1)
    assert controller.get_offline_release_count('pandas') == 1
    controller.update_release_count('pandas', 10)
    assert controller.get_offline_release_count('pandas') == 10

def test_download_latest(controller):
    assert isinstance(controller.download_latest('pandas'), dict)

def test_get_online_release_count(controller):
    assert isinstance(controller.get_online_release_count('pandas'), int)

def test_update(controller):
    controller.update('tensorflow')
    controller.assert_update('tensorflow')
    controller.update('pandas')
    controller.assert_update('pandas')
    controller.update('numpy')
    controller.assert_update('numpy')