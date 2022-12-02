from typing import Protocol

import brazilian_business_partner_api


class DB(Protocol):
    def connect(self):
        ...

    def execute(self, logger: brazilian_business_partner_api.Logger, query: str):
        ...
