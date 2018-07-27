import psycopg2
import os
import time
from datetime import datetime

if os.environ.get('RADHA') == "KRISHNA":
    conn = psycopg2.connect(database="bhagavadgita", user="radhakrishna",
                            password="BankeBihari100", host="139.59.20.51", port="5432")

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
