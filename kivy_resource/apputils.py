import urllib
import json
import os

from kivy.core.window import Window
# from kivy.lang import Builder
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.snackbar import Snackbar
from kivymd.app import MDApp

URL_TIMEOUT = 5


def load_kv(module_name):
    # Builder.load_file(f"{os.path.join(*module_name.split('.'))}.kv")
    app = MDApp.get_running_app()
    if app:
        app.KV_FILES.append(f"{os.path.join(*module_name.split('.'))}.kv")


class Notify(Snackbar):
    def __init__(self, **kwargs):
        text = kwargs.get('text', '')
        snack_type = kwargs.get('snack_type', 'success')
        bg_color = (.8, 0, 0, 1) if snack_type == 'error' else (0, .6, 0, 1)
        super().__init__(text=text,
                         bg_color=bg_color,
                         size_hint_x=(Window.width - (dp(10) * 2)) / Window.width,
                         snackbar_x="10dp",
                         snackbar_y="10dp"
                         )


def fetch(url, callback=None, **kwargs):
    on_error = kwargs.pop('on_error', None)
    method = kwargs.pop('method', 'GET')
    cookie = kwargs.pop('cookie', None)

    kw_params = kwargs.pop('params', {})
    params = buildParams(kw_params)

    def request_error(request, result):
        Notify(text=f"Server error {request.resp_status}: {result}", snack_type='error').open()
        if on_error:
            on_error(request, result)

    try:
        req_args = {'url': url if len(params) == 0 else f"{url}{params}",
                    'method': method,
                    'timeout': URL_TIMEOUT,
                    'on_failure': on_error if on_error else request_error,
                    'on_error': request_error
                    }

        if callback:
            req_args['on_success'] = callback

        if method in ['PUT', 'POST', 'DELETE']:
            data = kwargs.pop('data', None)
            if data:
                req_args['req_body'] = json.dumps(data)

        if method == 'DELETE':
            req_args['cookies'] = cookie if cookie else ''
        elif method in ['PUT', 'POST']:
            req_args['req_headers'] = {'Cookie': cookie if cookie else '', 'Content-type': 'application/json'}
        else:  # GET
            req_args['req_headers'] = {'Cookie': cookie if cookie else '', 'Accept': 'application/json'}

        return UrlRequest(**req_args)

    except Exception as e:
        print(e)
        if on_error:
            on_error(str(e), "Fetch Error")


def buildParams(param_dict: dict):
    param_list = [f"&{key}={urllib.parse.quote_plus(val)}" for key, val in param_dict.items() if val]
    params = ''.join(param_list)
    return f"?{params[1:]}" if len(params) > 0 else ''


def auth_exec(cookie, callback):
    rest_endpoint = os.environ['REST_ENDPOINT']
    fetch(f"{rest_endpoint}/ping", callback, cookie=cookie, on_error=lambda rq, rp: False)
