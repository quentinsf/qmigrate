#! /usr/bin/env python
#
# A very simple MySQL migrations system.
# See README.md for more info.
#
# This software is released under the GNU GPL v2 license.
# See LICENSE for details.
#
# (c) Q.Stafford-Fraser, Telemarq Ltd 2015

import os
import sys
import argparse
import glob
# We're assuming MySQL here:
import MySQLdb
from _mysql_exceptions import *

# Where do we find the migration scripts to execute?
MIGRATION_DIR = os.path.dirname(os.path.abspath(__file__))
# How do we create the 'migration' table if it doesn'x exist?
MIGRATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS `{t}` (
  `filename` text NOT NULL
)
"""

def main():
    parser = argparse.ArgumentParser(description='Perform new SQL commands on a database')
    parser.add_argument('--host',     required=False, default='localhost', help='The MySQL host')
    parser.add_argument('--port',     required=False, type=int, default=3306, help='The MySQL port')
    parser.add_argument('--user',     required=True, help='The MySQL user')
    parser.add_argument('--password', required=True, help='The MySQL password')
    parser.add_argument('--database', required=True, help='The MySQL database')
    parser.add_argument('--migrate_table', default='migrate', help='Table name to be used by migration system')
    args = parser.parse_args()

    # We're using MySQL here - it should be easy to modify this for other databases
    db = MySQLdb.connect(host=args.host, user=args.user, port=args.port, passwd=args.password, db=args.database)
    c = db.cursor()

    # First - does the database know about this migrate system?
    c.execute('SHOW TABLES')
    tables = [r[0] for r in c.fetchall()]
    migrate_table = args.migrate_table
    db_initialised = (migrate_table in tables)
    if not db_initialised:
        print "Creating table '%s' for use by the migration system." % migrate_table
        c.execute(MIGRATION_TABLE_SQL.format(t=migrate_table))
    c.close()

    # Which files have already been executed on this database?
    c = db.cursor()
    c.execute("SELECT * from `{t}`".format(t=migrate_table))
    already_run = [r[0] for r in c.fetchall()]
    c.close()

    # Now look at the SQL and Python migration files in this directory
    # Which must start with a digit and end with .sql or .py.
    os.chdir(MIGRATION_DIR)
    migration_files = glob.glob("[0-9]*.sql") + glob.glob("[0-9]*.py")
    migration_files.sort()
    for fn in migration_files:
        if fn not in already_run:

            succeeded = False
            print "Running", fn, ":",

            # If this is a SQL file, load it and execute the text

            if fn.endswith('.sql'):
                with open(fn, 'r') as f:
                    sql = f.read()
                    try:
                        c = db.cursor()
                        print c.execute(sql),"rows affected"
                        c.fetchall()
                        c.close()
                        succeeded = True
                    except ProgrammingError, e:
                        print >>sys.stderr, e
                        db.close()
                        sys.exit(1)

            # If this is a Python file, just execute it.
            # It will (deliberately) not inherit any of this environment
            # except the command-line args 'args'.

            else:
                execfile(fn, {'args':args}, {})
                succeeded = True

            if succeeded:
                c = db.cursor()
                c.execute("INSERT INTO `{t}` VALUES (%s)".format(t=migrate_table), (fn,))
                c.close()
                db.commit()

    db.commit()
    db.close()



if __name__ == '__main__':
    main()