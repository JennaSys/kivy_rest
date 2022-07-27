import os

from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty
from kivymd.app import MDApp

from apputils import fetch, Notify, load_kv

load_kv(__name__)


class BookEdit(Screen):
    book_id = NumericProperty()

    def open(self, book_id=None):
        app = MDApp.get_running_app()
        self.ids.save_edit.disabled = not app.is_auth()
        app.switch_screen('edit')

        self.book_id = book_id if book_id else -1
        if book_id:
            rest_endpoint = os.environ['REST_ENDPOINT']
            fetch(f"{rest_endpoint}/books/{book_id}", self.load_data)

    def close(self, ref):
        self.clear()
        app = MDApp.get_running_app()
        app.sm.get_screen('books').open()

    def load_data(self, request, result):
        book_data = result.get('book', None)
        if book_data:
            self.book_id = book_data['id']
            self.ids.title.text = book_data['title']
            self.ids.author.text = book_data['author']

    def handle_save(self):
        body = {'title': self.ids.title.text, 'author': self.ids.author.text}
        if self.book_id > 0:
            body['id'] = self.book_id

        rest_resource = "books" if self.book_id < 0 else f"books/{self.book_id}"
        method = 'POST' if self.book_id < 0 else 'PUT'
        app = MDApp.get_running_app()
        rest_endpoint = os.environ['REST_ENDPOINT']

        fetch(f"{rest_endpoint}/{rest_resource}", self.save_success, method=method, data=body, cookie=app.session_cookie)

    def save_success(self, request, result):
        Notify(text=f"Book {'added' if self.book_id < 0 else 'updated'}").open()
        self.clear()
        app = MDApp.get_running_app()
        app.sm.get_screen('books').get_books()
        app.sm.get_screen('books').open()

    def clear(self):
        self.book_id = -1
        self.ids.title.text = ""
        self.ids.author.text = ""