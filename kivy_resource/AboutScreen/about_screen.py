from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from kivy_resource.apputils import load_kv

load_kv(__name__)


class AboutScreen(MDScreen):
    @staticmethod
    def open():
        app = MDApp.get_running_app()
        app.switch_screen('about')

    @staticmethod
    def close(ref=None):
        app = MDApp.get_running_app()
        app.sm.get_screen('resources').open()
