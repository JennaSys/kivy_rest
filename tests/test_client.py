from .conftest import *
from dataclasses import dataclass

class MockClient(RestClient):
    def __init__(self, method, route, keys=[]):

        super().__init__(route.split('/')[0], keys)
        self.method = method
        self.route = route


    def call(self, method, route, callback, body=None):
    	assert method == self.method
    	assert route == self.route
    	return body

@dataclass
class MockWidget:
    text: str

BOOK_IDS = { 'title':MockWidget("Moby"),'author':MockWidget("Melville") }

def no_callback():
	assert False

def test_client():
	client = RestClient.Default()
	assert client
	assert client.keys
	assert client.keys[0] == 'title'

def test_client_extract():
	client = RestClient.Default()
	book = client.ids_text(BOOK_IDS)
	book['id'] = 1
	fields = client.extract(book)
	assert fields['resource_id'] == 1
	assert fields.get('text') == book['title']
	assert fields.get('secondary_text') == book['author']


def test_mock():
	mock = MockClient('PUT', '/')
	assert mock
	assert mock.method == 'PUT'
	assert mock.route == '/'
	result = mock.call('PUT', '/', None)
	assert result == None

def test_ids_text():
	mock = MockClient('POST', 'books', ['a'])
	ids = {'a': MockWidget('b')}
	result = mock.post(no_callback, ids)
	assert result.get('a') == 'b'

# fetch(f"{rest_endpoint}/ping", callback, cookie=cookie, on_error=lambda rq, rp: False)
def test_ping():
	mock = MockClient('GET', 'ping')
	result = mock.ping(no_callback)

# fetch(f"{rest_endpoint}/login", self.login_success, method='POST', data=body, on_error=login_error)
def test_login():
	mock = MockClient('POST', 'login')
	result = mock.login(no_callback, 'user', 'pw')
	assert result.get('username') == 'user'
	assert result.get('password') == 'pw'

# fetch(f"{rest_endpoint}/books", _load_data, on_error=_on_error)
def test_get_all():
	mock = MockClient('GET', 'books')
	result = mock.get(no_callback)

def test_get_one():
	mock = MockClient('GET', 'books/1')
	result = mock.get(no_callback, 1)

# fetch(f"{rest_endpoint}/{rest_resource}", self.save_success, method=method, data=body, cookie=app.session_cookie)
def test_post():
	mock = MockClient('POST', 'books', ['title','author'])
	result = mock.post(no_callback, BOOK_IDS)
	assert result.get('title') == 'Moby'
	assert result.get('author') == 'Melville'

def test_put():
	mock = MockClient('PUT', 'books/1', ['title','author'])
	result = mock.put(no_callback, BOOK_IDS, 1)
	assert result.get('title') == 'Moby'
	assert result.get('author') == 'Melville'

# fetch(f"{REST_ENDPOINT}/books/{self.resource_id}", self.delete_success, method='DELETE', cookie=app.session_cookie)
def test_delete():
	mock = MockClient('DELETE', 'books/1')
	mock.delete(no_callback, 1)


