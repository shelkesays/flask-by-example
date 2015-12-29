MOCK_USERS = {}

class MockDBHelper:

    def get_user(self, email):
        if email in MOCK_USERS:
            return MOCK_USERS[email]

    def add_user(self, email, salt, hashed):
        MOCK_USERS[email] = {'salt': salt, 'hashed': hashed}
