import json
from typing import Any
from urllib.parse import urljoin

from requests import Session, Request, Response
from requests.exceptions import JSONDecodeError


class ElsomBaseAPI:
    base_url: str

    def __init__(self):
        assert self.base_url

        self.session = Session()
        self.close = self.__exit__

    def setup_session(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def send_request(self, method: str, path: str, **params) -> Any:
        request = Request(method=method, url=urljoin(self.base_url, path), **params)
        self.process_request(request)
        response = self.session.send(request.prepare())
        return self.process_response(response)

    def process_request(self, request: Request) -> None:
        pass

    def process_response(self, response: Response) -> Any:
        try:
            return response.json()
        except JSONDecodeError:
            response.raise_for_status()

    def get(self, path: str, **params) -> Any:
        return self.send_request(method='GET', path=path, **params)

    def post(self, path: str, **params) -> Any:
        return self.send_request(method='POST', path=path, **params)


class ElsomAPI(ElsomBaseAPI):
    base_url = 'https://elsom.kg/api/'

    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self._pwd = password
        self.api_key: str = ''

    def _auth(self) -> None:
        payload = json.dumps({'username': self.username, 'password': self._pwd})
        request = Request(method='POST', url=urljoin(self.base_url, 'v1/auth/'), data=payload)
        data = self.process_response(self.session.send(request.prepare()))
        self.api_key = data['token']

    def process_request(self, request: Request) -> None:
        if not self.api_key:
            self._auth()

        request.headers['Authorization'] = 'Token ' + self.api_key
        request.headers['Content-Type'] = 'application/json'

    def generate_opt(self):
        return self.get(path='v1/generate_opt', params={'q': 'balalga'})


with ElsomAPI('adsd', 'fasdf') as api:
    api.generate_opt()

el = ElsomAPI('asd', 'asd')
el.generate_opt()
# el.close(None, None, None)
el.session.close()
