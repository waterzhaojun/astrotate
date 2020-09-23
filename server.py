import psycopg2
import json
import os
import getpass
from sqlalchemy import create_engine

def get_config(servername = 'awslevylab'):
    path = os.path.join(os.path.dirname(__file__), 'lib', 'server_config.json')
    with open(path, 'r') as f:
        config = json.load(f)
    return(config)

def server_engine(servername = 'awslevylab'):
    try:
        config = get_config()[servername]
        if config['password'] is None:
            config['password'] = input('Input password: ')
    except:
        config = {}
        config['server'] = input('server: ')
        config['database'] = input('database name: ')
        config['user'] = input('username: ')
        config['password'] = getpass.getpass('password: ')
        tmp = input('port (press Enter for 5432):')
        if tmp == '':
            config['port'] = '5432'

    # Connecting to PostgreSQL by providing a sqlachemy engine
    engine = create_engine('postgresql://'+config['user']+':'+config['password']+'@'+config['server']+':'+config['port']+'/'+config['database'],echo=False)
    return(engine)

def connect_server(servername = 'awslevylab'):
    try:
        config = get_config()[servername]
        if config['password'] is None:
            config['password'] = input('Input password: ')
    except:
        config = {}
        config['server'] = input('server: ')
        config['database'] = input('database name: ')
        config['user'] = input('username: ')
        config['password'] = getpass.getpass('password: ')
        tmp = input('port (press Enter for 5432):')
        if tmp == '':
            config['port'] = '5432'
    
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