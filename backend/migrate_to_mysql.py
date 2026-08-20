import sqlite3
import pymysql
import os

sqlite_db = '/home/mirrorwebs/Desktop/ai_interview/backend/interview_coach.db'
mysql_conn = pymysql.connect(
    host='localhost',
    user='root',
    password='admin1123',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with mysql_conn.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS `interview_coach` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute("CREATE DATABASE IF NOT EXISTS `interview_coach.` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    mysql_conn.select_db('interview_coach')

    if os.path.exists(sqlite_db):
        conn_sq = sqlite3.connect(sqlite_db)
        conn_sq.row_factory = sqlite3.Row
        cur_sq = conn_sq.cursor()

        cur_sq.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r['name'] for r in cur_sq.fetchall()]

        print(f"Migrating tables from SQLite: {tables}")

        with mysql_conn.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            for table in tables:
                cur_sq.execute(f"PRAGMA table_info({table});")
                cols = cur_sq.fetchall()
                
                # Build MySQL CREATE TABLE syntax
                col_defs = []
                for col in cols:
                    cname = col['name']
                    ctype = col['type'].upper()
                    if 'INT' in ctype:
                        mtype = 'INT'
                    elif 'BOOLEAN' in ctype or 'BOOL' in ctype:
                        mtype = 'TINYINT(1)'
                    elif 'TEXT' in ctype:
                        mtype = 'TEXT'
                    elif 'DATETIME' in ctype or 'TIMESTAMP' in ctype:
                        mtype = 'DATETIME'
                    else:
                        mtype = 'VARCHAR(255)'

                    if col['pk']:
                        mtype += ' PRIMARY KEY'
                        if 'INT' in mtype:
                            mtype += ' AUTO_INCREMENT'

                    col_defs.append(f"`{cname}` {mtype}")

                create_sql = f"CREATE TABLE IF NOT EXISTS `{table}` ({', '.join(col_defs)}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
                cursor.execute(create_sql)

                # Migrate data
                cur_sq.execute(f"SELECT * FROM `{table}`;")
                rows = cur_sq.fetchall()
                if rows:
                    col_names = [col['name'] for col in cols]
                    placeholders = ', '.join(['%s'] * len(col_names))
                    insert_sql = f"INSERT IGNORE INTO `{table}` (`{ '`, `'.join(col_names) }`) VALUES ({placeholders})"
                    
                    val_rows = []
                    for r in rows:
                        val_rows.append([r[k] for k in col_names])
                    cursor.executemany(insert_sql, val_rows)

            cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
            mysql_conn.commit()
            print("Successfully migrated data to MySQL `interview_coach`!")
finally:
    mysql_conn.close()
