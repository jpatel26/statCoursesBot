import pandas as pd
import pymysql
from .config import user, passwd, db, host


def load_synonym_table():
    return load_into_df('SELECT * FROM syn;')


def load_questions():
    return load_into_df('SELECT * FROM questions')


def load_into_df(select_query):
    conn = pymysql.connect(user=user, passwd=passwd, database=db, host=host)
    try:
        df = pd.read_sql(select_query, conn)
        return df
    finally:
        conn.close()
