import psycopg2
import argparse
import json
import util

parser = argparse.ArgumentParser(description='terminate a cage in table transgenic_animal_log.')
parser.add_argument('--cageid', required=True, help='Cage id')

args = parser.parse_args()

if __name__ == "__main__":
    
    conn = util.connect_server()

    cur = conn.cursor()
    cur.execute("""UPDATE transgenic_animal_log SET cageid = 'terminated' WHERE cageid = '{}';""".format(args.cageid))
    conn.commit()

    print('===== Cage %s terminated. =====' % args.cageid)