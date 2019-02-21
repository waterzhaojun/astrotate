import psycopg2
import argparse

parser = argparse.ArgumentParser(description='terminate a cage in table transgenic_animal_log.')
parser.add_argument('--cageid', required=True, help='Cage id')
parser.add_argument('--server', default='localhost', help='Server host')
parser.add_argument('--database', default='levy_lab_data', help='database name')
parser.add_argument('--user', default='postgres', help='username')
parser.add_argument('--password', default = None, help='password')

args = parser.parse_args()


def main(cageid = args.cageid, server = args.server, 
         database = args.database, user = args.user, password = args.password):
    conncommend = "host={} dbname={} user={}".format(server, database, user)
    # print(conncommend)
    conn = psycopg2.connect(conncommend)

    cur = conn.cursor()
    cur.execute("""UPDATE transgenic_animal_log SET cageid = 'terminated' WHERE cageid = '{}';""".format(cageid))
    conn.commit()

    print('===== Cage %s terminated. =====' % cageid)



if __name__ == "__main__":
    main()