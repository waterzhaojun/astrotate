import psycopg2
import json

def get_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return(config)

def connect_server(servername = 'elephantsql'):
    config = get_config()[servername]
    
    if config['password'] is None:
        config['password'] = input('Input password: ')
    
    conncommend = "host={} dbname={} user={} password={} port={}".format(config['server'], config['database'], config['user'], config['password'], config['port'])
    conn = psycopg2.connect(conncommend)
    return(conn)

def cageid2mateid(cageid):
    conn = connect_server()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT cageid FROM transgenic_mouse_breeding
        WHERE inprocess = true;
        """)
    records = cur.fetchall()
    conn.commit()
    print(records)