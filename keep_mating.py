import psycopg2
import argparse

parser = argparse.ArgumentParser(description='Create a mate record for table transgenic_mouse_breeding.')
parser.add_argument('--mateid', required=True, help='the original mateid you want to keep mating')
parser.add_argument('--server', default='localhost', help='Server host')
parser.add_argument('--database', default='levy_lab_data', help='database name')
parser.add_argument('--user', default='postgres', help='username')
parser.add_argument('--password', default = None, help='password')

args = parser.parse_args()

def matestyle(num):
    style = 'M' + '%04d' % (num)
    return(style)

def main(mateid = args.mateid, server = args.server, 
         database = args.database, user = args.user, password = args.password):
    conncommend = "host={} dbname={} user={}".format(server, database, user)
    # print(conncommend)
    conn = psycopg2.connect(conncommend)

    cur = conn.cursor()
    cur.execute(
    """
    SELECT mateid FROM {}
    """.format('transgenic_mouse_breeding')
    )
    mateids = cur.fetchall()
    conn.commit()

    mateids = [x[0] for x in mateids]
    mateids.sort()

    newmate = matestyle(int(mateids[-1][1:])+1)
    print(newmate)

    # get the record
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM transgenic_mouse_breeding where mateid = '{}';
        """.format(mateid))
    record = cur.fetchall()[0]
    conn.commit()
    print(record)
    
    # set old record inprocess to false
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE transgenic_mouse_breeding SET inprocess = false WHERE mateid = '{}';
        """.format(mateid))
    conn.commit()


    # insert a new record using same information as old record
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO transgenic_mouse_breeding (mateid, cageid, father_id, mother_id, pair_date, inprocess) 
        VALUES ('{}', '{}', '{}', '{}', '{}', '{}');
        """.format(newmate, record[1], record[2], record[3], record[4], 'true')
    )
    conn.commit()
    
    print('input done')

    cur = conn.cursor()
    cur.execute(
    """
    SELECT * FROM transgenic_mouse_breeding
    WHERE mateid = '{}'
    
    """.format(newmate)
    )
    tmp = cur.fetchall()
    conn.commit()
    print(tmp)



if __name__ == "__main__":
    main()