import psycopg2
import argparse
import numpy as np
import transgenic_offspring_name_style as namestyle
import util

parser = argparse.ArgumentParser(description='Weaning small mice from a cage and build animal log for them \
    in table transgenic_animal_log.')
parser.add_argument('--mateid', required=True, help='Mate id')
parser.add_argument('--malenum', required=True, type = int, help='young male mice number')
parser.add_argument('--femalenum', required=True, type = int, help='yound female mice number')
parser.add_argument('--malecage', required = True, help='which cage yound males go')
parser.add_argument('--femalecage', required=True, help='which cage yound females go')
parser.add_argument('--keepMate', default = False, help='whether still mating')

args = parser.parse_args()

def matestyle(num):
    style = 'M' + '%04d' % (num)
    return(style)

def get_new_mateid(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT mateid FROM transgenic_mouse_breeding;
        """)
    records = cur.fetchall()
    conn.commit()

    records.sort()
    return matestyle(int(records[-1][0][1:])+1)


def main(mateid = args.mateid, mnum = args.malenum, fnum = args.femalenum, 
         mcage = args.malecage, fcage = args.femalecage, keepMate = args.keepMate):

    conn = util.connect_server()

    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM transgenic_mouse_breeding 
        WHERE mateid = '{}';
        """.format(mateid))
    records = cur.fetchall()
    conn.commit()

    # transfer an object to a dict. It is easier for possible position change in the future.
    record = {}
    record['mateid'] = records[0][0]
    record['cageid'] = records[0][1]
    record['fatherid'] = records[0][2]
    record['motherid'] = records[0][3]
    record['pair_date'] = records[0][4]
    record['birthday'] = records[0][5]

    try:
        father_title = namestyle.name_title(record['fatherid'])
    except:
        father_title = None
    
    try:
        mother_title = namestyle.name_title(record['motherid'])
    except:
        mother_title = None

    offspring_title = namestyle.offspring_title([father_title, mother_title])
    print('offspring title is %s.' % offspring_title)

    baseSeq = offspring_title+'-'+record['birthday'].strftime('%y%m')+str(int(mateid[1:]))

    sexSeq = np.append(['M']*mnum, ['F']*fnum)
    cageSeq = np.append([mcage]*mnum, [fcage]*fnum)

    for i in range(len(sexSeq)):
        tmp_newname = baseSeq+'%02d'%(i)
        insertcommand = """
        INSERT INTO transgenic_animal_log (animalid, cageid, dob, gender, birth_mate_id, full_name)
        VALUES ('{}', '{}', '{}', '{}', '{}', '{}')
        """.format(tmp_newname, cageSeq[i], record['birthday'], sexSeq[i], record['mateid'], tmp_newname)

        cur = conn.cursor()
        cur.execute(insertcommand)
        conn.commit()
        print('%s insert done' % (baseSeq+'%02d'%(i)))

    cur = conn.cursor()
    cur.execute(
        """
        UPDATE transgenic_mouse_breeding 
        SET inprocess = false, weaning_date = current_date
        WHERE mateid = '{}';
        """.format(record['mateid']))
    conn.commit()

    # if keep mating, add a new mating record
    if keepMate:
        new_mateid = get_new_mateid(conn)

        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO transgenic_mouse_breeding (mateid, cageid, father_id, mother_id, pair_date, inprocess)
            VALUEs ('{}', '{}', '{}', '{}', '{}', {});
            """.format(new_mateid, record['cageid'], record['fatherid'], record['motherid'], 
                       record['pair_date'], 'true'))
        conn.commit()



if __name__ == "__main__":
    main()