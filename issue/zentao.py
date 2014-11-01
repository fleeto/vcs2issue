import datetime

__author__ = 'dustise'

import re

import MySQLdb

from issue.base import Base


class Zentao(Base):
    def __init__(self):
        Base.__init__(self)

    __DataBase = None

    Product = 0

    Project = 0

    @staticmethod
    def commit_info_pattern():
        return '''\[(\S+):(\d+):(\S):(\S+)\]'''

    @staticmethod
    def commit_info_message():
        info = """
        'Commit info should include [type:task_id:action:next]'
        type: 'task' or 'bug'
        id: number
        action:
            o - keep original
            r - solved
            c - closed
        next: next user
        """
        return info

    def search_issue(self, issue_id, issue_type='bug'):
        sql = ''
        if issue_type == 'bug':
            sql = 'SELECT * FROM zt_bug WHERE id= %s' % issue_id

        if issue_type == 'task':
            sql = 'SELECT * FROM zt_task WHERE id=%s' % issue_id
        cursor = self.__DataBase.cursor()
        res = cursor.execute(sql)
        return res > 0

    def search_user(self, user_id):
        sql = "SELECT * FROM zt_user WHERE account='%s'" % user_id
        cursor = self.__DataBase.cursor()
        res = cursor.execute(sql)
        return res > 0

    def update_issue(self, issue_id, new_status):
        return Base.update_issue(self, issue_id, new_status)

    def set_url(self, url):
        Base.set_url(self, url)
        url_parser = re.compile('''mysql...(\S+):(\S+)@(\S+):(\d+)/(\S+)''')
        match = url_parser.search(self.db_url)
        group = match.groups()
        user = group[0]
        password = group[1]
        host = group[2]
        port = int(group[3])
        db = group[4]
        self.__DataBase = MySQLdb.connect(host=host,
                                          user=user,
                                          passwd=password,
                                          port=port,
                                          db=db)

    @staticmethod
    def parse_comment(comment):
        expr = re.compile(Zentao.commit_info_pattern())
        result = expr.search(comment)
        if result is None:
            return False
        gp = result.groups()
        return gp[0], gp[1], gp[2], gp[3]

    def __submit_bug(self, bug_id, next_account):
        sql = "UPDATE zt_bug SET status='resolved', resolution='fixed', resolvedDate='%s'," \
              " resolvedBy= '%s', assignedTo='%s', assignedDate='%s', lastEditedBy='%s', " \
              " lastEditedDate='%s'" \
              " WHERE id = %d"
        sql %= (self.__current_date(), self.my_account, next_account, self.__current_date(),
                self.my_account, self.__current_date(), bug_id)
        cursor = self.__DataBase.cursor()
        return cursor.execute(sql)

    def __submit_task(self, task_id, next_account):
        sql = "UPDATE zt_task " \
              "SET status='done', assignedTo='%s', assignedDate='%s', " \
              "lastEditedBy='%s', lastEditedDate='%s'" \
              "WHERE id= %d"
        sql %= (next_account, self.__current_date(),
                self.my_account, self.__current_date(), task_id)
        cursor = self.__DataBase.cursor()
        return cursor.execute(sql)

    @staticmethod
    def __current_date():
        return datetime.datetime.now().strftime('%Y-%m-%d %X')

    def __write_history(self, obj_type, obj_id, comment):
        object_type = obj_type
        if obj_type == 'task':
            object_type = 'story'
        sql = "INSERT INTO " \
              "zt_action (objectType, objectID, product, " \
              "project, actor, action, date, extra,comment) " \
              "VALUES ('%s', %s, %s, %s, '%s', 'edited', '%s', 'vcs' ,'<p>from vcs: </p> %s')"
        sql %= (object_type, obj_id, self.Product,
                self.Project, self.my_account, self.__current_date(), comment)
        cursor = self.__DataBase.cursor()
        return cursor.execute(sql) > 0

    def process_comment(self, comment):
        (obj_type, obj_id, action, account) = self.parse_comment(comment)
        obj_id = int(obj_id)
        self.__write_history(obj_type, obj_id, comment)
        if action == 'o':
            return True
        if obj_type == 'task':
            return self.__submit_task(obj_id, account)
        if obj_type == 'bug':
            return self.__submit_bug(obj_id, account)
