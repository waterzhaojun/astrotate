import psycopg2
import argparse
import json
import util

parser = argparse.ArgumentParser(description='Create a mate record for table transgenic_mouse_breeding.')
# parser.add_argument('--dad', required=True, help='Father id')
# parser.add_argument('--mom', required=True, help='Mother id')
parser.add_argument('--cageid', required=True, help='Cage id')

args = parser.parse_args()

def matestyle(num):
    style = 'M' + '%04d' % (num)
    return(style)

def next_mateid(conn):
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
    return(newmate)

def animals_from_cage(conn, cageid):
    cur = conn.cursor()
    cur.execute(
    """
    SELECT animalid, gender FROM transgenic_animal_log WHERE cageid = '{}'
    """.format(cageid)
    )
    animals = cur.fetchall()
    conn.commit()

    return(animals)

def check_mate(conn, mateid):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT mateid, cageid, father_id, mother_id, pair_date FROM transgenic_mouse_breeding 
        WHERE mateid = '{}'
        """.format(mateid)
        )
    mate = cur.fetchall()
    conn.commit()
    if len(mate) != 1:
        raise Exception('This mateid length is not 1.')
    print('mateid: %s, cageid: %s, father id: %s, mother id: %s, pair date: %s' % (mate[0][0], mate[0][1], mate[0][2], mate[0][3], mate[0][4]))
    

def main(cageid = args.cageid):

    conn = util.connect_server()

    animals = animals_from_cage(conn, cageid)
    father = [x for x in animals if x[1] == 'M']
    mother = [x for x in animals if x[1] == 'F']

    if len(father) != 1:
        raise Exception('We need and only need 1 male animal. Please check the cage.')
    fatherid = father[0][0]

    for i in range(len(mother)):
        nextmateid = next_mateid(conn)
        motherid = mother[i][0]

        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO transgenic_mouse_breeding (mateid, cageid, father_id, mother_id, pair_date, inprocess) 
            VALUES ('{}', '{}', '{}', '{}', current_date, true);
            """.format(nextmateid, cageid, fatherid, motherid)
        )
        conn.commit()
    
        print('insert done')
        check_mate(conn, nextmateid)


if __name__ == "__main__":

    main()