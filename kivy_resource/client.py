import os
from kivy_resource.apputils import fetch
from kivymd.app import MDApp

class RestClient():

    def Default():
        resource = os.environ['REST_RESOURCE']
        keys = os.environ['REST_KEYS'].split(',')
        return RestClient(resource, keys)

    def __init__(self, resource, id_keys):
        self.resource = resource
        self.keys = id_keys # Name Detail

    def extract(self, data):
        FIELDS = ['text','secondary_text', 'resource_id']
        values = [data[k] for k in self.keys]
        fields = dict(zip(FIELDS, values))
        fields[FIELDS[2]] = data['id']
        return fields

    def ids_text(self, ids):
        return {k: ids[k].text for k in self.keys}

    def ping(self, callback):
        url = 'ping'
        return self.call('GET', url, callback)

    def login(self, callback, username, password):
        options = {'username': username, 'password': password}
        url = 'login'
        return self.call('POST', url, callback, options)

    def logout(self, callback):
        url = 'logout'
        return self.call('POST', url, callback)

    def get(self, callback, resource_id=None, **kwargs):
        url = f"{self.resource}/{resource_id}" if resource_id else self.resource 
        return self.call('GET', url, callback, kwargs)

    def post(self, callback, ids,**kwargs):
        options = self.ids_text(ids) | kwargs
        url = self.resource
        return self.call('POST', url, callback, options)

    def put(self, callback, ids, resource_id, **kwargs):
        options = self.ids_text(ids) | kwargs
        options['id'] = resource_id
        url = f"{self.resource}/{resource_id}"
        return self.call('PUT', url, callback, options)

    def delete(self, callback, resource_id, **kwargs):
        url = f"{self.resource}/{resource_id}"
        return self.call('DELETE', url, callback)

    def call(self, method, route, callback, options=None):
        endpoint = os.environ['REST_ENDPOINT']
        app = MDApp.get_running_app()
        url = f"{endpoint}/{route}"
        params = {
            'method': method,
            'options': options,
            'cookie': app.session_cookie,
        } | options
        return fetch(url, callback, **params)