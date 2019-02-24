import psycopg2
import argparse
import numpy as np
import transgenic_offspring_name_style as namestyle

parser = argparse.ArgumentParser(description='Weaning small mice from a cage and build animal log for them \
    in table transgenic_animal_log.')
parser.add_argument('--mateid', required=True, help='Mate id')
parser.add_argument('--malenum', required=True, type = int, help='young male mice number')
parser.add_argument('--femalenum', required=True, type = int, help='yound female mice number')
parser.add_argument('--malecage', required = True, help='which cage yound males go')
parser.add_argument('--femalecage', required=True, help='which cage yound females go')
parser.add_argument('--server', default='localhost', help='Server host')
parser.add_argument('--database', default='levy_lab_data', help='database name')
parser.add_argument('--user', default='postgres', help='username')
parser.add_argument('--password', default = None, help='password')

args = parser.parse_args()




def main(mateid = args.mateid, mnum = args.malenum, fnum = args.femalenum, 
         mcage = args.malecage, fcage = args.femalecage, server = args.server, 
         database = args.database, user = args.user, password = args.password):

    conncommend = "host={} dbname={} user={}".format(server, database, user)
    # print(conncommend)
    conn = psycopg2.connect(conncommend)

    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM transgenic_mouse_breeding 
        WHERE mateid = '{}';
        """.format(mateid))
    record = cur.fetchall()
    conn.commit()

    record = record[0]
    try:
        father_title = namestyle.name_title(record[2])
    except:
        father_title = None
    
    try:
        mother_title = namestyle.name_title(record[3])
    except:
        mother_title = None

    offspring_title = namestyle.offspring_title([father_title, mother_title])
    print('offspring title is %s.' % offspring_title)

    birthday = record[5]
    baseSeq = offspring_title+'-'+birthday.strftime('%y%m')+str(int(mateid[1:]))

    sexSeq = np.append(['M']*mnum, ['F']*fnum)
    cageSeq = np.append([mcage]*mnum, [fcage]*fnum)

    for i in range(len(sexSeq)):
        insertcommand = """
        INSERT INTO transgenic_animal_log (animalid, cageid, dob, gender, birth_mate_id)
        VALUES ('{}', '{}', '{}', '{}', '{}')
        """.format(baseSeq+'%02d'%(i), cageSeq[i], birthday, sexSeq[i], mateid)
        # print(insertcommand)

        cur = conn.cursor()
        cur.execute(insertcommand)
        conn.commit()
        print('%s insert done' % (baseSeq+'%02d'%(i)))



if __name__ == "__main__":
    main()