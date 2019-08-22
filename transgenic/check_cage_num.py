import psycopg2
import util
import numpy as np

def cagestyle(num):
    style = 'C' + '%03d' % (num)
    return(style)

def main():
    conn = util.connect_server()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT cageid FROM transgenic_animal_log 
        """
        )
    cageids = cur.fetchall()
    conn.commit()
    cageids = [x[0] for x in cageids]
    cageids = list(set(cageids))
    cageids = [int(x[1:]) for x in cageids if x != 'terminated']
    cageids.sort()
    print(cageids)
    maxid = max(cageids)
    available_num = np.array([])
    for i in range(1, maxid):
        if i not in cageids:
            available_num = np.append(available_num, i)
    available_cages = [cagestyle(x) for x in available_num]
    print('total cage num: %d' % len(cageids))
    print('maxid: %d' % maxid)
    print('available nums: %s', available_cages)

if __name__ == "__main__":

    main()