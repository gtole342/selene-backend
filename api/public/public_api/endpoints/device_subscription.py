from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.account import AccountRepository
from selene.util.db import get_db_connection


class DeviceSubscriptionEndpoint(SeleneEndpoint):
    def __init__(self):
        super(DeviceSubscriptionEndpoint, self).__init__()

    def get(self, device_id):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            account = AccountRepository(db).get_account_by_device_id(device_id)
        if account:
            subscription = account.subscription
            response = {'@type': subscription.type if subscription is not None else 'free'}, HTTPStatus.OK
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response