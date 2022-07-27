import os

from kivy.app import App
from kivy.uix.screenmanager import Screen
from apputils import load_kv, Notify, fetch

load_kv(__name__)


class LoginScreen(Screen):
    @staticmethod
    def login():
        app = App.get_running_app()
        app.switch_screen('login')

    @staticmethod
    def cancel_login():
        app = App.get_running_app()
        app.switch_screen('books')

    def clear(self):
        self.ids.username.text = ""
        self.ids.password.text = ""

    def logout(self):
        app = App.get_running_app()
        app.menu.dismiss()

        def on_success(request, result):
            Notify(text="Logged out").open()

        app = App.get_running_app()
        rest_endpoint = os.environ['REST_ENDPOINT']
        fetch(f"{rest_endpoint}/logout", on_success, cookie=app.session_cookie)

        app.session_cookie = None

        app.menu.add_item(id="login", text="Login", icon="login", on_release=self.login)
        app.menu.remove_item('logout')

    def do_login(self):
        username = self.ids.username.text
        password = self.ids.password.text

        def login_error(request, result):
            Notify(text="Login failed!", snack_type='error').open()

        body = {'username': username, 'password': password}
        rest_endpoint = os.environ['REST_ENDPOINT']
        fetch(f"{rest_endpoint}/login", self.login_success, method='POST', data=body, onError=login_error)

        self.clear()

    def login_success(self, request, result):
        app = App.get_running_app()
        app.session_cookie = request.resp_headers.get('Set-Cookie', None)
        Notify(text="Login successful!").open()
        app.switch_screen('books')

        app.menu.add_item(id="logout", text="Logout", icon="logout", on_release=self.logout)
        app.menu.remove_item('login')
