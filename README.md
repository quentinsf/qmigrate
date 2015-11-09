# QMigrate - A very simple ORM-independent migration system!

I wrote this when converting a PHP-based project into Python.  I wanted a source-controlled record of the changes I was making to the database in the PHP world, so that when the Python code was ready I could run the same commands on the current database before switching over.  

It's like a really cut-down version of Django's migration system.

Here's how it works:

* You add to this directory a set of SQL or Python files to be executed.  
  They should begin with a digit, and end with .sql or .py.

* There is a table in the database listing which ones *have* been executed.
  This is called 'migrate' by default, but can be changed with an option.

Now, when you run `migrate.py`, it will do the following:

     
    Create the 'migrate' table if it doesn't exist
    
    For each *.sql or *.py file in the directory, in alphanumeric order:
    
        If the filename is not listed in the table, then:
    
            * run the file
            * if successful, record its name in the table
     

Example usage:

    migrate.py \
        --host myhost --database mydb \
        --user myuser --password mypassword

It's normally easy to run this as part of your deployment process.

This script assumes a MySQL database, and hence the 'MySQL-python' package needs to be installed, but it should be trivial to modify the script for other databases if needed.


-- (c) Q.Stafford-Fraser, Telemarq Ltd 2015

