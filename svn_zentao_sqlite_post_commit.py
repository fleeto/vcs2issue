#!/usr/bin/python

"""
Sample post-commit file:

#!/bin/sh

REPOSITORY="$1"
REV="$2"
TXN_NAME="$3"
PROJECT=1
PRODUCT=1

/path/svn_zentao_sqlite_post_commit.py "$PROJECT" "PRODUCT" "$REPOSITORY" "$REV"  \
 "mysql://user:pass@localhost:3306/zentao" "/usr/share/svn.sqlite"

"""

import sys

from vcs.subversion import SvnLook
from issue.zentao import Zentao
from record.sqlite_record import SqliteRecord


def main(product, project, repo, rev, zentao_db, sqlite_db):
    zt = Zentao()
    zt.set_url(zentao_db)
    zt.Product = product
    zt.Project = project
    sl = SvnLook()
    sl.target = rev

    sl.target_type = "r"
    sl.repository = repo
    svn_log = sl.get_log()
    res = zt.parse_comment(svn_log)
    (obj_type, obj_id, action, account) = res

    author = sl.get_author()
    diff = sl.get_diff()
    changed = sl.get_changed()

    zt.my_account = author
    zt.process_comment(svn_log)

    rec = SqliteRecord(sqlite_db)

    rec.write_action(author, diff, changed, obj_type + "_" + obj_id, repo, rev)

    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) < 5:
        sys.stderr.write("Usage: %s Product_ID Project_ID Repository_path TXN zentao_db_url sqlite_db_file\n"
                         % (sys.argv[0]))
        sys.exit(1)
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
