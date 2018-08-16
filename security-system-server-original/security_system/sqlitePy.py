import sqlite3

conn = sqlite3.connect('db.sqlite3')
conn.execute(
    "insert into knowledgeBase_instance (name,ins_type,ip,city,country,lat,lon,port,timestamp) values('test','Camera','test','test','test','50','85','test','test')")
conn.commit()
conn.close()
