import psycopg2
import util
import argparse
import numpy as np

parser = argparse.ArgumentParser(description='Create a mate record for table transgenic_mouse_breeding.')
parser.add_argument('-c', '--cageid', required=True, help='Cage id')
args = parser.parse_args()

if __name__ == "__main__":

    punch = ['L', 'R', 'none', 'LR', 'LL', 'RR']
    cageid = args.cageid
    conn = util.connect_server()

    cur = conn.cursor()
    cur.execute(
        """
        SELECT animalid FROM transgenic_animal_log
        WHERE cageid='{}'
        """.format(cageid))
    records = cur.fetchall()
    conn.commit()

    records = [x[0] for x in records]
    records.sort()
    
    if len(records) < 3:
        punch = np.append(punch[0:len(records)-1], 'none')

    for i in range(len(records)):
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE transgenic_animal_log
            SET ear_punch = '{}'
            WHERE animalid='{}'
            """.format(punch[i], records[i]))
        conn.commit()
        print('set %s %s ear punch as %s' % (cageid, records[i], punch[i]))
