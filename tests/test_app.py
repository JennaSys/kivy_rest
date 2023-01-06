from .conftest import *

from kivy.config import Config
from kivy.config import ConfigParser
from kivy.uix.settings import Settings
from kivy.lang import Builder

def test_app():
	app = MainApp()
	config = ConfigParser()
	app.build_config(Config)
	s = Settings()
	app.build_settings(s)
	Builder.load_file('./kivy_resource/mainapp.kv')
	sm = app.build_app(True)
	assert app