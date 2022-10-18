# an example of search sqlite with regular expression

import re, os
try:
    import apsw
    apswInstalled = True
except:
    import sqlite3
    apswInstalled = False

def regexp(expr, item):
    reg = re.compile(expr, flags=re.IGNORECASE)
    return reg.search(item) is not None

def checkRegexp():
    file = os.path.join("marvelData", "bibles", "KJV.bible")
    if os.path.exists(file):
        if apswInstalled:
            connection = apsw.Connection(file)
            connection.createscalarfunction("REGEXP", regexp)
        else:
            connection = sqlite3.connect(file)
            connection.create_function("REGEXP", 2, regexp)
        cursor = connection.cursor()
        query = "SELECT * FROM Verses WHERE Scripture REGEXP ?"
        cursor.execute(query, ("jesus.*?love",))
        print(cursor.fetchall())

checkRegexp()
