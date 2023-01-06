import os

from kivy.factory import Factory
from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty
from kivymd.app import MDApp

from kivy_resource.apputils import Notify, load_kv
from kivy_resource.client import RestClient

load_kv(__name__)


class ResourceEdit(MDScreen):
    resource_id = NumericProperty(None, allownone=True)


    def open(self, resource_id=None):
        app = MDApp.get_running_app()
        authorized = app.is_auth()
        self.ids.save_edit.disabled = not authorized
        for field in self.ids.edit_fields.children:
            if isinstance(field, Factory.ResourceField):
                field.cursor = (0, 0)
                field.disabled = not authorized

        self.ids.title.focus = True
        app.switch_screen('edit')

        self.resource_id = resource_id
        if resource_id is not None:
            rest_endpoint = os.environ['REST_ENDPOINT']
            RestClient.Default().get(self.load_data, resource_id)

    def close(self, ref=None):
        self.clear()
        app = MDApp.get_running_app()
        app.sm.get_screen('resources').open()

    def load_data(self, request, result):
        resource_data = result.get('book', None)
        if resource_data:
            self.resource_id = resource_data['id']
            self.ids.title.text = resource_data['title']
            self.ids.author.text = resource_data['author']

    def handle_save(self):
        body = {'title': self.ids.title.text, 'author': self.ids.author.text}
        if self.resource_id is not None:
            body['id'] = self.resource_id
            return RestClient.Default().put(self.save_success, body)
        return RestClient.Default().post(self.save_success, body)

    def save_success(self, request, result):
        Notify(text=f"Resource {'added' if self.resource_id is None else 'updated'}").open()
        self.clear()
        app = MDApp.get_running_app()
        app.sm.get_screen('resources').list_resources()
        app.sm.get_screen('resources').open()

    def clear(self):
        self.resource_id = None
        self.ids.title.text = ""
        self.ids.author.text = ""
