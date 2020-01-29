from astrotate import server, utils, config

def add_nb():
    address = input('Address: ')
    title = input('Title: ')
    description = input('Description: ')
    cg = config.Config()
    author = utils.select('Author: ', cg.operator, 0)
    conn = server.connect_server()
    cur = conn.cursor()
    cur.execute(
    """
    INSERT INTO projects (path, description, title, author)
    VALUES ('{}', '{}', '{}', '{}')
    """.format(address, description, title, author)
    )
    conn.commit()
    conn.close()

#class notebook():
#    def __init__(self):
#        self.