from kivymd.app import MDApp
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.card import MDCardSwipe


class Book(MDCardSwipe):
    book_id = NumericProperty()
    text = StringProperty()
    secondary_text = StringProperty()

    def handle_select(self):
        if self.open_progress == 0.0:
            print(f"Clicked {self.book_id}!")

    def handle_delete(self):
        if self.open_progress > 0.0:
            print(f"Delete {self.book_id}!")


class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Pink"
        pass

    def on_start(self):
        for i in range(10):
            self.root.ids.books.add_widget(
                Book(book_id= i, text=f"Book title {i}", secondary_text="author")
            )


if __name__ == '__main__':
    app = MainApp()
    app.run()
