import os

from kivymd.uix.card import MDCardSwipe
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty
from kivy.app import App

from apputils import fetch, Notify, load_kv

load_kv(__name__)


class ConfirmDialog(MDDialog):
    def __init__(self, title, text="", on_ok=None):
        app = App.get_running_app()
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


class BookList(Screen):
    @staticmethod
    def handle_addnew():
        app = App.get_running_app()
        app.sm.get_screen('edit').open()


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
        app = App.get_running_app()
        REST_ENDPOINT = os.environ['REST_ENDPOINT']

        fetch(f"{REST_ENDPOINT}/books/{self.book_id}", self.delete_success, method='DELETE', cookie=app.session_cookie)

    @staticmethod
    def delete_success(request, result):
        Notify(text="Book deleted").open()
        app = App.get_running_app()
        app.get_books()

    def handle_delete(self):
        if self.open_progress > 0.0:
            self.dialog.open()

    def handle_edit(self, book_id):
        if self.open_progress == 0.0:
            app = App.get_running_app()
            app.sm.get_screen('edit').open(book_id)
