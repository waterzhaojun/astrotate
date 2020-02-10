from astrotate import server, utils, config


class Notebook():
    def __init__(self, pid=None):
        conn = server.connect_server()
        if pid == None:
            self.path = input('Address: ')
            self.title = input('Title: ')
            self.description = input('Description: ')
            cg = config.Config()
            self.author = utils.select('Author: ', cg.operator, 0)
            self.main = int(input('main: '))
            self.type = utils.select('type: ', ['paper', 'analysis', 'tech'])
            
            cur = conn.cursor()
            cur.execute(
            """
            INSERT INTO projects_nb (path, description, title, author, main, type)
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}')
            RETURNING pid
            """.format(self.path, self.description, self.title, self.author, self.main, self.type)
            )
            pid = cur.fetchone()
            conn.commit()
            self.pid = pid[0]
        else:
            self.pid = pid
            cur = conn.cursor()
            cur.execute(
            """
            SELECT path, description, title, author, main, type from projects_nb
            WHERE pid = '{}'
            """.format(self.pid)
            )
            tmp = cur.fetchone()
            conn.commit()
            self.path = tmp[0]
            self.description = tmp[1]
            self.title = tmp[2]
            self.author = tmp[3]
            self.main = tmp[4]
            self.type = tmp[5]

        conn.close()