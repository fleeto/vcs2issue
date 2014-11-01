__author__ = 'dustise'


class Base:
    def __init__(self):
        pass

    db_url = ''
    my_account = ''

    @staticmethod
    def commit_info_message():
        raise NotImplementedError

    @staticmethod
    def commit_info_pattern():
        raise NotImplementedError

    def set_url(self, url):
        self.db_url = url

    def search_issue(self, issue_id, issue_type='bug'):
        raise NotImplementedError

    def update_issue(self, issue_id, new_status):
        raise NotImplementedError

    def process_comment(self, comment):
        raise NotImplementedError

    def search_user(self, user_id):
        raise NotImplementedError