from sqlite3 import connect
from utils import DB_NAME
from models.user import User
from models.request import Request
from utils import INTEREST_LIST
from data import serialize


class Db:
    __db = None

    def __init__(self):
        self.connection = connect(DB_NAME, check_same_thread=False)
        self.c = self.connection.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name VARCHAR(40),
        instagram VARCHAR(100),
        gender INTEGER ,
        batch VARCHAR(40),
        connected INTEGER
        )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS requests (
                id INTEGER REFERENCES users(id),
                to_id INTEGER REFERENCES users(id),
                status INTEGER
                )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS interest(
        id INTEGER PRIMARY KEY,
        interest VARCHAR(20)
        )""")

        for i in range(len(INTEREST_LIST)):
            self.c.execute("""INSERT OR IGNORE INTO interest (id,interest) values (?,?)""", (i, INTEREST_LIST[i]))
        self.connection.commit()

        self.c.execute("""CREATE TABLE IF NOT EXISTS user_interest(
        id INTEGER REFERENCES users(id),
        interest INTEGER REFERENCES interest(id)
        )""")

    @staticmethod
    def get_instance():
        serialize()
        if Db.__db is None:
            Db.__db = Db()
        return Db.__db

    def read_users(self):
        self.c.execute("""SELECT * FROM users""")
        users = []
        for user in self.c.fetchall():
            new_user = User(user[0])
            new_user.make(user[1], user[3], user[2], user[4])
            new_user.connected = user[5]
            users.append(new_user)
        for user in users:
            print(user.name)

    def read_requests(self):
        self.c.execute("""SELECT * FROM requests""")
        requests = []
        for request in self.c.fetchall():
            new_request = Request()
            new_request.make(request[0], request[1], request[2])
            requests.append(new_request)
        for request in requests:
            print(request.tel_to)

    def read_user_id(self, tel_id: int) -> User:
        self.c.execute("""SELECT * FROM users WHERE id=?""", (tel_id,))
        data = self.c.fetchone()
        if data:
            user = User(data[0])
            user.make(data[1], data[3], data[2], data[4])
            user.connected = data[5]
            return user
        return None

    def read_available_users(self, tel_id: int):
        self.c.execute("""SELECT * FROM users WHERE connected=0 AND id != ?""", (tel_id,))
        users = []
        for user in self.c.fetchall():
            new_user = User(user[0])
            new_user.make(user[1], user[3], user[2], user[4])
            new_user.connected = user[5]
            users.append(new_user)
        return users

    def read_request_id(self, tel_id: int) -> Request:
        self.c.execute("""SELECT * FROM requests WHERE id=? OR to_id=?""", (tel_id, tel_id))
        data = self.c.fetchone()
        if data:
            request = Request()
            request.make(data[0], data[1], data[2])
            return request
        return None

    def write_user(self, user):
        self.c.execute("""INSERT INTO users (id,name,instagram,gender,batch,connected ) VALUES  (?,?,?,?,?,?)""",
                       (user.tel_id, user.name,
                        user.instagram_id,
                        user.gender,
                        user.batch,
                        user.connected))

        self.connection.commit()

    def update_user_connected(self, tel_id: int):
        self.c.execute("""UPDATE users SET connected = 1 WHERE id = ?""", (tel_id,))
        self.connection.commit()

    def update_user_disconnected(self, tel_id: int):
        self.c.execute("""UPDATE users SET connected = 0 WHERE id = ?""", (tel_id,))
        self.connection.commit()

    def write_request(self, request: Request):
        self.c.execute("""INSERT INTO requests (id,to_id,status ) VALUES  (?,?,?)""",
                       (request.tel_id, request.tel_to,
                        request.status))

        self.connection.commit()

    def update_request(self, request: Request):
        self.c.execute("""UPDATE requests SET status = ? WHERE id = ? AND to_id = ?""",
                       (request.tel_id, request.tel_to,
                        request.status))

        self.connection.commit()

    def add_interest(self, user_id, i):
        self.c.execute("""INSERT INTO user_interest (id,interest) VALUES (?,?)""", (user_id, i))
        self.connection.commit()

    def get_common_interests(self, user_id_1, user_id_2):
        user_1 = set()
        user_2 = set()
        self.c.execute("""SELECT * FROM user_interest WHERE id==? OR id ==?""", (user_id_1, user_id_2))
        for i in self.c.fetchall():
            if i[0] == user_id_1:
                user_1.add(i[1])
            else:
                user_2.add(i[1])
        return [user_1, user_2]

    def __del__(self):
        self.c.close()
        self.connection.close()
