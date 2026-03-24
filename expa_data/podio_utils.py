import os
import time
import requests


class PodioService:
    def __init__(self, app_id=None, app_token=None):
        self.client_id = os.getenv('PODIO_CLIENT_ID', 'mc-task')
        self.client_secret = os.getenv('PODIO_CLIENT_SECRET', '')
        self.username = os.getenv('PODIO_USERNAME', '')
        self.password = os.getenv('PODIO_PASSWORD', '')
        self.app_id = str(app_id or os.getenv('PODIO_APP_ID', ''))
        self.app_token = app_token or os.getenv('PODIO_APP_TOKEN', '')

        self.access_token = None
        self.token_expires = 0

    def _auth_app_token(self):
        if not self.app_token:
            return False

        payload = {
            'grant_type': 'app',
            'app_id': self.app_id,
            'app_token': self.app_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post('https://podio.com/oauth/token', data=payload, timeout=20)
        if response.status_code != 200:
            return False

        data = response.json()
        self.access_token = data.get('access_token')
        self.token_expires = int(time.time()) + int(data.get('expires_in', 0))
        return bool(self.access_token)

    def _auth_password(self):
        payload = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post('https://podio.com/oauth/token', data=payload, timeout=20)
        if response.status_code != 200:
            return False

        data = response.json()
        self.access_token = data.get('access_token')
        self.token_expires = int(time.time()) + int(data.get('expires_in', 0))
        return bool(self.access_token)

    def ensure_authenticated(self):
        if self.access_token and time.time() < self.token_expires - 60:
            return True

        if self._auth_app_token():
            return True

        return self._auth_password()

    def create_item(self, fields_data):
        if not self.ensure_authenticated():
            return False, 'podio_auth_failed'

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
        payload = {'fields': fields_data}
        response = requests.post(
            f'https://api.podio.com/item/app/{self.app_id}',
            json=payload,
            headers=headers,
            timeout=30,
        )

        if response.status_code in (200, 201, 204):
            return True, response.text

        return False, response.text
