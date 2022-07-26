from kivy.uix.screenmanager import Screen
from apputils import load_kv

load_kv(__name__)


class LoginScreen(Screen):
    def clear(self):
        self.ids.username.text = ""
        self.ids.password.text = ""
