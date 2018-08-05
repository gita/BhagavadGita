import psycopg2
import os
import time
from datetime import datetime 

myFile = open(
    '/home/radhakrishna/radhakrishna/append.txt', 'a')
myFile.write('\nAccessed on ' + str(datetime.now()))  

conn = psycopg2.connect(database=os.environ.get('DB'), user=os.environ.get('DB_USER'),
                        password=os.environ.get('DB_PASSWORD'), host=os.environ.get('DB_HOST'), port=os.environ.get('DB_PORT'))

print("Opened database successfully")

cur = conn.cursor()

ts = time.time()
today = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
sql = """
    SELECT *
    FROM verse_of_day
    WHERE timestamp::date = date '%s'
    LIMIT 1
""" % (today)
cur.execute(sql)
verse = cur.fetchall()

if verse == []:
    sql = """
            INSERT INTO verse_of_day (chapter_number, verse_number)
            SELECT chapter_number, verses.verse_number
            FROM verses ORDER BY random() LIMIT 1
    """
    cur.execute(sql)
    conn.commit()

conn.close()
