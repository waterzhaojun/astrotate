# THis function is to add a window set up record for in vivo animal which is used for 2 photon.

import psycopg2
import argparse
import datetime
import numpy as np

parser = argparse.ArgumentParser(description='Create a window setup record for in vivo animals.')
parser.add_argument('--animalid', required=True, help='the animal to setup window')
parser.add_argument('--date', default='today', help='the date do this surgery')
parser.add_argument('--server', default='localhost', help='Server host')
parser.add_argument('--database', default='levy_lab_data', help='database name')
parser.add_argument('--user', default='postgres', help='username')
parser.add_argument('--password', default = None, help='password')

args = parser.parse_args()

def main(animalid = args.animalid, date = args.date, server = args.server, 
         database = args.database, user = args.user, password = args.password):

    conncommend = "host={} dbname={} user={}".format(server, database, user)
    conn = psycopg2.connect(conncommend)

    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM in_vivo_image_animal WHERE animalid = '{}'
        """.format(animalid)
    )
    record = cur.fetchall()[0]
    conn.commit()

    if date == 'today':
        date = datetime.date.today().strftime('%m-%d-%Y')
    else:
        date = date # datetime.date.strptime(date, '%m-%d-%Y')
    print(date)


    process = record[4]['treatment']
    process = np.append(process, {'step': 'window setup', 'window_type_setup_date': date})
    print(process)

    cur = conn.cursor()
    cur.execute(
        """
        UPDATE in_vivo_image_animal
        SET process = process :: jsonb || {}
        WHERE animalid = '{}'
        """.format(process, animalid)
    )
    #conn.commit()



if __name__ == "__main__":
    main()