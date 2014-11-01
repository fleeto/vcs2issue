import os

from misc.utils import Utils


__author__ = 'dustise'


class SvnLook:
    def __init__(self, base_path="/usr/local/Cellar/subversion/1.8.10_1/bin/"):
        self.look_command = os.path.join(base_path, "svnlook")
        self.repository = ""
        self.target = ""
        self.target_type = "r"

    @staticmethod
    def __is_text(file_name):
        txt_file = ['htm', 'ini', 'conf', 'mxml',
                    'txt', 'xml', 'ps', 'php',
                    'java', 'phtml', 'html', 'css', 'js', 'jsp', 'sql', 'wsdl',
                    'info', 'bat', 'sh', 'xsd']

        ext = os.path.os.path.splitext(file_name)
        return (len(ext) < 5) and (txt_file.count(ext) > 0)

    @staticmethod
    def __get_look_result(cmd_path, sub_command, repos, para):
        cmd = '%s %s %s %s' % (cmd_path, sub_command, para, repos)
        return Utils.exec_command(cmd)

    def __format_result(self, s):
        return_list = s.split("\n")
        from string import strip

        res = filter(None, map(strip, return_list))
        file_changed = {}
        for line in res:
            file_name = line[2:]
            file_action = line[0]
            file_size = 0
            if (file_action == "A") and (SvnLook.__is_text(file_name)):
                file_content = self.get_content(file_name)
                file_size = len(file_content.split("\n"))
            file_changed[file_name] = "%s %d" % (file_action, file_size)

        return file_changed

    def get_log(self):
        ret = self.__get_look_result(self.look_command, "log",
                                     "-%s %s" % (self.target_type, self.target),
                                     self.repository)
        return ret

    def get_author(self):
        ret = self.__get_look_result(self.look_command, "author",
                                     "-%s %s" % (self.target_type, self.target),
                                     self.repository)
        return ret.strip()

    def get_changed(self):
        ret = self.__get_look_result(self.look_command, "changed",
                                     "-%s %s" % (self.target_type, self.target),
                                     self.repository)
        import sys

        sys.stderr.write("---\n" + ret + "---\n")
        return self.__format_result(ret)

    def get_diff(self):
        ret = self.__get_look_result(self.look_command, "diff",
                                     "-%s %s" % (self.target_type, self.target),
                                     self.repository)
        return ret

    def get_content(self, file_name):
        ret = Utils.exec_command(
            '%s %s -%s %s %s %s' %
            (self.look_command, "cat", self.target_type,
             self.target, self.repository, file_name))
        return ret
