import urllib
import json

from kivy.network.urlrequest import UrlRequest
from kivymd.uix.snackbar import Snackbar


URL_TIMEOUT = 5


class Notify(Snackbar):
    def __init__(self, **kwargs):
        text = kwargs.get('text', '')
        snack_type = kwargs.get('snack_type', 'success')
        bg_color = (.8, 0, 0, 1) if snack_type == 'error' else (0, .6, 0, 1)
        super().__init__(text=text, bg_color=bg_color)


def fetch(url, callback=None, **kwargs):
    on_error = kwargs.pop('onError', None)
    method = kwargs.pop('method', 'GET')
    cookie = kwargs.pop('cookie', None)

    kw_params = kwargs.pop('params', {})
    params = buildParams(kw_params)

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

        req = UrlRequest(**req_args)

    except Exception as e:
        print(e)
        if on_error:
            on_error(str(e), "Fetch Error")


def request_error(request, result):
    Notify(text=f"Server error {request.resp_status}: {result}", snack_type='error').open()


def buildParams(param_dict: dict):
    param_list = [f"&{key}={urllib.parse.quote_plus(val)}" for key, val in param_dict.items() if val]
    params = ''.join(param_list)
    return f"?{params[1:]}" if len(params) > 0 else ''
