import psycopg2
import json
import os

def get_config():
    path = os.path.join(os.path.dirname(__file__), 'lib', 'server_config.json')
    with open(path, 'r') as f:
        config = json.load(f)
    return(config)

def connect_server(servername = 'elephantsql'):
    config = get_config()[servername]
    
    if config['password'] is None:
        config['password'] = input('Input password: ')
    
    conncommend = "host={} dbname={} user={} password={} port={}".format(config['server'], config['database'], config['user'], config['password'], config['port'])
    conn = psycopg2.connect(conncommend)
    return(conn)


def get_info_by_animalid(transgenic_id, con):
    conn = connect_server()
    cur = conn.cursor()
    cur.execute(
    """
    SELECT * FROM transgenic_animal_log
    WHERE animalid = '{}';
    """.format(transgenic_id)
    )
    record = cur.fetchall()
    conn.commit()
    conn.close()
    if len(record) > 0:
        record = record[0]
    else:
        record = None
    return(record)