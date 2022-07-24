from kivymd.app import MDApp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout


class Window(GridLayout):
    pass


class Book(BoxLayout):
    @staticmethod
    def on_press_button():
        print('You pressed the button!')


class MainApp(MDApp):
    def build(self):
        window = Window(rows=3)

        item_list = window.ids.item_list
        for _ in range(20):
            item_list.add_widget(Book())

        return window


if __name__ == '__main__':
    app = MainApp()
    app.run()
