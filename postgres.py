#!/usr/bin/env python
import psycopg2

from passwords import db_name, db_user, db_host, db_password

def getConnection() :
    con = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (db_name, db_user, db_host, db_password))
    return con

