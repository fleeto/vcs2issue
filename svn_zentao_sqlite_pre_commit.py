#!/usr/bin/python

"""
sample pre-commit file:

#!/bin/sh

REPOSITORY="$1"
TXN="$2"
/path/svn_zentao_sqlite_pre_commit.py "$REPOSITORY" "$TXN" "mysql://user:pass@localhost:3306/zentao"
"""

import sys

from vcs.subversion import SvnLook
from issue.zentao import Zentao


def main(repo, txn, zentao_db):
    zt = Zentao()
    zt.set_url(zentao_db)
    sl = SvnLook()
    sl.target = txn

    sl.target_type = "t"
    sl.repository = repo
    svn_log = sl.get_log()
    if len(svn_log) < 10:
        sys.stderr.write("Your message '%s' is too short(%d).\n" % (svn_log, len(svn_log)))
        sys.stderr.write("Please enter a commit message which details what has changed during this commit.")
        sys.exit(1)
    res = zt.parse_comment(svn_log)
    if not res:
        sys.stderr.write('Commit log \n %s \n is in an invalid format, the correct format is ' % svn_log
                         + Zentao.commit_info_message())
        sys.exit(1)
    (obj_type, obj_id, action, account) = res
    obj_id = int(obj_id)
    if not zt.search_issue(obj_id, obj_type):
        sys.stderr.write('the issue id %d of type %s is invalid.'
                         % (obj_id, obj_type))
        sys.exit(1)
    my_name = sl.get_author()
    if not zt.search_user(my_name):
        sys.stderr.write('You subversion user name %s does not exist in Zentao.' % my_name)
        sys.exit(1)
    if not zt.search_user(account):
        sys.stderr.write('You are trying to assign the issue to  %s, but the user does not exist in zentao.' % account)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.stderr.write("Usage: %s Repository_path TXN db_url\n" % (sys.argv[0]))
        sys.exit(1)
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
