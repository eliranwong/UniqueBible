import os, apsw
from uniquebible import config
from uniquebible.util.GitHubRepoInfo import GitHubRepoInfo


class UserRepoSqlite:

    TABLE_NAME = "UserRepo"
    CREATE_TABLE = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME}
        (id Integer Primary Key Autoincrement,
        active Integer,
        name NVARCHAR(100),
        type NVARCHAR(20),
        repo NVARCHAR(200),
        directory NVARCHAR(100))
        """

    def __init__(self):
        self.filename = os.path.join(config.marvelData, "userrepo.sqlite")
        self.connection = apsw.Connection(self.filename)
        self.cursor = self.connection.cursor()
        if not self.checkTableExists():
            self.createTable()

    def __del__(self):
#        #self.cursor.execute("COMMIT")
        self.connection.close()

    def createTable(self):
        self.cursor.execute(UserRepoSqlite.CREATE_TABLE)

    def checkTableExists(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}'".format(self.TABLE_NAME))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def insert(self, name, type, repo, directory="", active=True):
        repo = GitHubRepoInfo.fixRepoUrl(repo)
        insert = f"""INSERT INTO {self.TABLE_NAME} 
            (active, name, type, repo, directory) 
            VALUES (?, ?, ?, ?, ?)"""
        self.cursor.execute(insert, (active, name, type, repo, directory))
#        self.cursor.execute("COMMIT")

    def update(self, id, name, type, repo, directory="", active=True):
        repo = GitHubRepoInfo.fixRepoUrl(repo)
        update = f"""UPDATE {self.TABLE_NAME} SET
            active=?, name=?, type=?, repo=?, directory=?
            WHERE id=?"""
        self.cursor.execute(update, (active, name, type, repo, directory, id))
#        self.cursor.execute("COMMIT")

    def delete(self, id):
        delete = f"DELETE FROM {self.TABLE_NAME} WHERE id=?"
        self.cursor.execute(delete, (id,))
#        self.cursor.execute("COMMIT")

    def deleteAll(self):
        delete = f"DELETE FROM {self.TABLE_NAME}"
        self.cursor.execute(delete)
#        self.cursor.execute("COMMIT")

    def getAll(self):
        query = f"SELECT id, active, name, type, repo, directory FROM {self.TABLE_NAME} order by name"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def checkRepoExists(self, name, type, repo, directory):
        query = f"SELECT * FROM {self.TABLE_NAME} WHERE name=? and type=? and repo=? and directory=?"
        self.cursor.execute(query, (name, type, repo, directory))
        if self.cursor.fetchone():
            return True
        else:
            return False


if __name__ == "__main__":

    config.marvelData = "/home/oliver/dev/UniqueBible/marvelData/"
    # config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"

    db = UserRepoSqlite()
    # db.deleteAll()
    db.insert("my bible 3", "pdf", "pdf/testing3", "custom")
    repos = db.getAll()
    for repo in repos:
        print(f"{repo[0]}:{repo[1]}:{repo[2]}:{repo[3]}:{repo[4]}:{repo[5]}")
    # db.update(repo[0], "update bible", "bibles", "otseng/testing2", "custom", False)
    # repos = db.getAll()
    # for repo in repos:
    #     print(f"{repo[0]}:{repo[1]}:{repo[2]}:{repo[3]}:{repo[4]}:{repo[5]}")
