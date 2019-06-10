import config as cfg
import pandas as pd
import pymysql


def load_synonym_table():
    return load_into_df('SELECT * FROM syn;')


def load_questions():
    return load_into_df('SELECT * FROM questions')


def load_into_df(select_query):
    conn = pymysql.connect(user=cfg.user, passwd=cfg.passwd, database=cfg.db, host=cfg.host)
    try:
        df = pd.read_sql(select_query, conn)
        return df
    finally:
        conn.close()
