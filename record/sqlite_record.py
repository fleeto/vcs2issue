# coding=utf-8
import re
import sqlite3
import uuid

__author__ = 'dustise'


class SqliteRecord:
    database = ''

    def __init__(self, db_url):
        self.database = db_url

    def write_action(self, author, diff, changed, bug_id, repos, revision):
        # 参数解析
        file_changed = {}
        for line in changed:
            line = re.sub("\s+", " ", line).strip()
            file_action = line[0]
            file_name = line[2:]
            file_changed[file_name] = file_action
        diff_lines = self.__diff_summary(diff)  # 变更行数

        for file_name, file_diff in changed.items():
            diff_lines += int(file_diff[2:])
        if author == "":
            author = "None"
        action_id = str(uuid.uuid4())
        sql_list = []
        action_sql = ("INSERT INTO actions\n"
                      "(action_id, bug_id, file_count, line_count, author, repos, revision)\n"
                      "VALUES (\"%s\", \"%s\", %d, %d, \"%s\", \"%s\", %d)")
        sql_list.append(action_sql % (action_id, bug_id, len(changed),
                                      diff_lines, author, repos, int(revision)))
        for file_name, file_diff in changed.items():
            file_action = file_diff[0]
            diff_lines += int(file_diff[2:])
            file_sql = """INSERT INTO files (action_id, filepath, change_type)
            VALUES ("%s", "%s", "%s")"""
            file_sql = file_sql % (action_id, file_name.strip(), file_action)
            sql_list.append(file_sql)
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        for sql in sql_list:
            # sys.stderr.write(sql + "\n")
            cursor.execute(sql)
        conn.commit()
        conn.close()

    def get_update_summary(self, first_day, last_day):
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = "SELECT * FROM actions where action_time > '%s' and action_time < '%s'"
        sql %= (first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d"))
        cur.execute(sql)
        row = cur.fetchone()
        # 开始统计
        action_count = 0
        total_line = 0
        total_file = 0
        bug_list = {}
        user_list = {}
        while row:
            action_count += 1
            # Bug计数
            bug_id = row["bug_id"]
            line_count = int(row["line_count"])
            file_count = int(row["file_count"])
            if not bug_id in bug_list:
                bug_list[bug_id] = 1
            else:
                bug_list[bug_id] += 1
            # 用户计数
            user = row["author"]
            if not user in user_list:
                user_list[user] = {}
                user_list[user]["actionCount"] = 1
                user_list[user]["bugList"] = []
                user_list[user]["lineCount"] = 0
                user_list[user]["fileCount"] = 0
            else:
                user_list[user]["actionCount"] += 1
            if not bug_id in user_list[user]["bugList"]:
                user_list[user]["bugList"].append(bug_id)
            user_list[user]["lineCount"] += line_count
            user_list[user]["fileCount"] += file_count
            total_line += line_count
            total_file += file_count
            row = cur.fetchone()
        summary = {"totalLine": total_line, "totalFile": total_file, "userList": user_list, "ticketList": bug_list}
        return summary

    @staticmethod
    def __diff_summary(diff):
        total_line = 0
        diff_list = diff.split("\n")
        import string

        diff_list = filter(None, map(string.strip, diff_list))
        for line in diff_list:
            if line[0] == "+" or line[0] == "-":
                total_line += 1
        return total_line
