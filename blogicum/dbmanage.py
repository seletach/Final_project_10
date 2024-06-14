import sqlite3

con = sqlite3.connect('db.sqlite3')

cur = con.cursor()

query_1 = '''
DELETE FROM blog_post WHERE id=40;
'''

cur.execute(query_1)
con.commit()
con.close() 