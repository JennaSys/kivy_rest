import os
import threading

from kivy.clock import mainthread, Clock
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty, StringProperty

from apputils import fetch, Notify, load_kv

load_kv(__name__)


class ConfirmDialog(MDDialog):
    def __init__(self, title, text="", on_ok=None):
        app = MDApp.get_running_app()
        kwargs = dict(
            title=title,
            text=text,
            type='confirmation',
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=app.theme_cls.primary_color,
                    on_release=lambda x: self.dismiss()
                ),
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=app.theme_cls.primary_color,
                    on_release=lambda val: on_ok()
                ),
            ])

        super().__init__(**kwargs)


class BookList(MDScreen):
    def show_add_btn(self, show=True):
        self.ids.add_btn.disabled = not show
        self.ids.add_btn.opacity = 1.0 if show else 0

    @staticmethod
    def handle_addnew():
        app = MDApp.get_running_app()
        app.sm.get_screen('edit').open()

    def on_enter(self):
        Clock.schedule_once(self.set_auth)

    def set_auth(self, dt=0):
        app = MDApp.get_running_app()
        authorized = app.is_auth()
        self.show_add_btn(authorized)
        for book in self.ids.booklist.children:
            if isinstance(book, Book):
                book.ids.del_btn.disabled = not authorized

    def open(self):
        app = MDApp.get_running_app()
        app.switch_screen('books')

    def get_books(self):
        app = MDApp.get_running_app()
        app.menu.dismiss()

        @mainthread
        def _load_data(request, result):
            book_data = result.get('books', None)
            if book_data:
                authorized = app.is_auth()
                for book in book_data:
                    new_book = Book(book_id=book['id'], text=book['title'], secondary_text=book['author'])
                    new_book.ids.del_btn.disabled = not authorized
                    self.ids.booklist.add_widget(new_book)

            self.ids.loading.active = False

        @mainthread
        def _clear_data():
            self.ids.loading.active = True
            self.ids.booklist.clear_widgets()

        @mainthread
        def _on_error(*args):
            self.ids.loading.active = False

        def _get_books():
            Clock.schedule_once(lambda dt: _clear_data(), 0)

            rest_endpoint = os.environ['REST_ENDPOINT']
            fetch(f"{rest_endpoint}/books", _load_data, on_error=_on_error)

        threading.Thread(target=_get_books).start()


class Book(MDCardSwipe):
    book_id = NumericProperty()
    text = StringProperty()
    secondary_text = StringProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.dialog = ConfirmDialog(title="Delete Book",
                                    text=f"Are you sure you want to permanently delete '{self.text}'?",
                                    on_ok=self.do_delete)

    def do_delete(self):
        self.dialog.dismiss()
        app = MDApp.get_running_app()
        REST_ENDPOINT = os.environ['REST_ENDPOINT']

        fetch(f"{REST_ENDPOINT}/books/{self.book_id}", self.delete_success, method='DELETE', cookie=app.session_cookie)

    @staticmethod
    def delete_success(request, result):
        Notify(text="Book deleted").open()
        app = MDApp.get_running_app()
        app.sm.get_screen('books').get_books()

    def handle_delete(self):
        if self.open_progress > 0.0:
            self.dialog.open()

    def handle_edit(self, book_id):
        if self.open_progress == 0.0:
            app = MDApp.get_running_app()
            app.sm.get_screen('edit').open(book_id)
