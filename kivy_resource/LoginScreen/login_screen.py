import os

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from kivy_resource.apputils import load_kv, Notify, fetch

load_kv(__name__)


class LoginScreen(MDScreen):
    def open(self):
        app = MDApp.get_running_app()
        self.ids.username.focus = True
        app.switch_screen('login')

    def close(self):
        self.clear()
        app = MDApp.get_running_app()
        app.sm.get_screen('books').open()

    def clear(self):
        self.ids.username.text = ""
        self.ids.password.text = ""

    def logout(self):
        app = MDApp.get_running_app()
        app.menu.dismiss()

        def on_success(request, result):
            Notify(text="Logged out").open()
            app.sm.get_screen('books').set_auth()
            app.sm.get_screen('books').open()

        app = MDApp.get_running_app()
        rest_endpoint = os.environ['REST_ENDPOINT']
        fetch(f"{rest_endpoint}/logout", on_success, cookie=app.session_cookie)

        app.session_cookie = None

        app.menu.add_item(id="login", text="Login", icon="login", on_release=self.open)
        app.menu.remove_item('logout')

    def do_login(self):
        def login_error(request, result):
            Notify(text="Login failed!", snack_type='error').open()

        body = {'username': self.ids.username.text, 'password': self.ids.password.text}
        rest_endpoint = os.environ['REST_ENDPOINT']
        fetch(f"{rest_endpoint}/login", self.login_success, method='POST', data=body, on_error=login_error)

        self.clear()

    def login_success(self, request, result):
        app = MDApp.get_running_app()
        app.session_cookie = request.resp_headers.get('Set-Cookie', None)
        Notify(text="Login successful!").open()
        app.sm.get_screen('books').open()

        app.menu.add_item(id="logout", text="Logout", icon="logout", on_release=self.logout)
        app.menu.remove_item('login')
