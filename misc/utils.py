__author__ = 'dustise'

import os
import subprocess


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def exec_command(cmd):
        p = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE)
        output, error_info = p.communicate()
        if len(error_info) > 0:
            return error_info
        else:
            return output

    @staticmethod
    def is_text(file_name):
        """
        :rtype : bool
        """
        text_file = ['htm', 'ini', 'conf', 'mxml', 'install', 'module', 'info',
                     'txt', 'xml', 'ps', 'php',
                     'java', 'phtml', 'html', 'css', 'js', 'jsp', 'sql', 'wsdl',
                     'info', 'bat', 'sh', 'xsd']
        ext = os.path.os.path.splitext(file_name)
        return (len(ext) > 1) and (text_file.count(ext[-1][1:]) > 0)