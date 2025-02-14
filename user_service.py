import sqlite3


class UserService:
    def __init__(self, db_name='store.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        self.cursor = self.conn.cursor()

    def add_user(self, username, password):
        self.cursor.execute('insert into user (username,password) values ( ?, ?)',
                            (username, password))
        self.conn.commit()

    def get_user(self, username, password=None):
        if password is None:
            self.cursor.execute('select id, username,password from user where username = ?', (username,))
            user = self.cursor.fetchone()
            self.conn.commit()
            return user

        self.cursor.execute('select id, username,password from user where username = ? and password = ?',
                            (username, password))
        user = self.cursor.fetchone()
        self.conn.commit()
        return user

    def close(self):
        self.conn.commit()
        self.conn.close()
