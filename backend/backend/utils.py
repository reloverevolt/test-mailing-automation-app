from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import requests


class MailingAPI:
    def __init__(self, config):
        self.token = config.token
        self.base_url = config.base_url
        self.headers = self.construct_headers()

    def construct_headers(self) -> Dict:
        headers = dict()
        headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def send_message(
        self, message_id: int, message_text: str, client_phone: int
    ) -> Tuple:

        message_id_str = str(message_id)
        request_url = "/".join([self.base_url, "send", message_id_str])

        data = {"id": message_id, "phone": client_phone, "text": message_text}

        response = requests.post(request_url, headers=self.headers, data=data)

        if not response.ok:
            return False, response.status_code

        return True, response.status_code


@dataclass
class MailingService:
    token: str
    base_url: str
    api: MailingAPI = field(init=False, default=None)

    def __post_init__(self):
        self.api = MailingAPI(config=self)


@dataclass
class Config:
    debug: bool
    django_secret_key: str
    django_static_url: str
    django_allowed_hosts: List[str]
    local_timezone: str
    mailing_service: MailingService
    stat_recipients: List[str]
