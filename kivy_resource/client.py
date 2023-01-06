import os
from kivy_resource.apputils import fetch
from kivymd.app import MDApp

class RestClient():

    def __init__(self, resource, id_keys):
        self.resource = resource
        self.keys = id_keys # Name Detail

    def ids_text(self, ids):
        return {k: ids[k].text for k in self.keys}

    def ping(self, callback):
        url = 'ping'
        return self.call('GET', url, callback)

    def login(self, callback, username, password):
        body = {'username': username, 'password': password}
        url = 'login'
        return self.call('POST', url, callback, body)

    def logout(self, callback):
        url = 'logout'
        return self.call('POST', url, callback)

    def get(self, callback, resource_id=None):
        url = f"{self.resource}/{resource_id}" if resource_id else self.resource 
        return self.call('GET', url, callback)

    def post(self, callback, ids):
        body = self.ids_text(ids)
        url = self.resource
        return self.call('POST', url, callback, body)

    def put(self, callback, ids, resource_id):
        body = self.ids_text(ids)
        body['id'] = resource_id
        url = f"{self.resource}/{resource_id}"
        return self.call('PUT', url, callback, body)

    def delete(self, callback, resource_id):
        url = f"{self.resource}/{resource_id}"
        return self.call('DELETE', url, callback)

    def call(self, method, route, callback, body=None):
        endpoint = os.environ['REST_ENDPOINT']
        app = MDApp.get_running_app()
        url = f"{endpoint}/{route}"
        options = {
            'method': method,
            'body': body,
            'cookie': app.session_cookie,
        }
        return fetch(url, callback, **options)

