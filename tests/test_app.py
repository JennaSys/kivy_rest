from kivy_resource.main import MainApp
from .conftest import *

def test_app():
	app = MainApp()
	assert app