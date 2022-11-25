import configparser
import mysql.connector
from mysql.connector import Error
import pandas as pd


class DB:
    def __init__(self):
        self.parser = configparser.ConfigParser()
        self.parser.read('sql.ini')

    def connect(self):
        try:
            conn = mysql.connector.connect(
                host=self.parser['Settings']['host'],
                user=self.parser['Settings']['user'],
                password=self.parser['Settings']['password']
            )
        except Error as e:
            print(e)
        else:
            return conn
