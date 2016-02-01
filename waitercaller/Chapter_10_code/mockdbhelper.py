import datetime

MOCK_USERS = {}
MOCK_TABLES = {'1': {'number':'1', 'owner':'t@t.com', 'url': 'mock url'}}
MOCK_REQUESTS = {'1':{'table_number':'1', 'time':datetime.datetime.now()}}


class MockDBHelper:

    def __init__(self, database):
		pass

    def get_user(self, email):
        if email in MOCK_USERS:
            return MOCK_USERS[email]

    def add_user(self, email, salt, hashed):
        MOCK_USERS[email] = {'salt': salt, 'hashed': hashed}

    def add_table(self, number, owner):
		MOCK_TABLES[number] = {'number':number, 'owner':owner}
		return number

    def update_table(self, _id, url):
		MOCK_TABLES[_id]['url'] = url

    def get_tables(self, owner_id):
		return MOCK_TABLES

    def get_table(self, table_id):
        for table in MOCK_TABLES:
            if table == table_id:
                return MOCK_TABLES[table]

    def delete_table(self, table_id):
        del MOCK_TABLES[table_id]

    def add_request(self, table_id, time):
        table_number = self.get_table(table_id)['number']
        MOCK_REQUESTS[table_id] = {'table_number':table_number, 'time':time}

    def get_requests(self, owner_id):
        return MOCK_REQUESTS

    def delete_request(self, request_id):
        del MOCK_REQUESTS[request_id]
