"""
functions in this file is to build a record for surgery animal.
Steps:
1. use init_animal(folder) to build based animal information in the surgery folder.
2. When we do some treatment, use add_treatment(animalid, folder, treatment) to add a treatment dict to this animal's treatment array.
3. When we want to add some note to this animal, use add_note(animalid, folder) to add note to this animal's note array. Each note in this array should be a list formated by 
   [date, value]. This method is under development.
"""

from datetime import datetime
from astrotate import utils, server
import json

class Animal():
    def __init__(self, animalid):
        self.__keys__ = ['animalid', 'cageid', 'ear_punch']
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
        """
        SELECT {} FROM transgenic_animal_log 
        WHERE animalid = '{}';
        """.format(', '.join(self.__keys__), animalid)
        )
        animal = cur.fetchall()
        conn.commit()

        if len(animal) == 0: # need to build new animal info
            raise ValueError('Does not have this animal')

        elif len(animal) == 1: # load animal info
            for i in range(len(self.__keys__)):
                setattr(self, self.__keys__[i], animal[0][i])

        conn.close()

    

    def terminate(self):
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
        """
        UPDATE transgenic_animal_log 
        SET cageid='terminated'
        WHERE animalid = '{}';
        """.format(self.animalid)
        )
        conn.commit()
        conn.close()

    def add_treatment(self, treatment):
        conn = server.connect_server()
        cur = conn.cursor()
        
        cur.execute(
            """
            INSERT INTO surg_treatment
            (animalid, date, method, operator, note, parameters)
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}')
            RETURNING serialid
            """.format(self.animalid, treatment.date, treatment.method, treatment.operator, treatment.note, json.dumps(treatment.parameters))
        )
        sid = cur.fetchone()
        sid = sid[0]
        print(sid)
        conn.commit()
        if hasattr(self, 'time'):
            cur.execute(
                """
                    UPDATE surg_treatment
                    SET time = '{}'
                    WHERE serialid = '{}'
                """.format(self.time, sid)
            )
            conn.commit()
        conn.close()
        if treatment.method == 'PFA purfusion':
            self.terminate()
        
    def mark_aavresult(self):
        conn = server.connect_server()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT parameters, serialid, date from surg_treatment
            WHERE animalid = '{}' and method = 'virus inject'
            """.format(self.animalid)
        )
        t = cur.fetchall()
        conn.commit()
        
        aavlist = [[x[0]['virus_id'] + ' (date: ' + x[2].strftime('%m-%d-%Y') + ')', x[0]['result'],x[1]] for x in t]
        aavlistforselect = [x[0] for x in aavlist]

        targetaav = utils.select('Select the AAV you want to mark the result. ', aavlistforselect, None)
        targetid = [x[2] for x in aavlist if x[0] == targetaav]
        if len(targetid) != 1:
            conn.close()
            raise Exception('please check treatment, why the selected aav length is not 1.')
        else:
            targetid = targetid[0]

        scorelist = ['No expression', 'only several fibers', 'only several areas', 'many areas, easy to find', 'many areas and multiple layers']
        score = utils.select('Score the %s result. Choose by idx: ' % targetaav, scorelist)
        score = scorelist.index(score)

        cur = conn.cursor()
        cur.execute(
            """
            UPDATE surg_treatment
            SET parameters = jsonb_set(parameters, '{}', '{}', FALSE)
            WHERE serialid = '{}'
            """.format('{result}',score, targetid)
            
        )
        conn.commit()
        conn.close()

        
    def do_earpunch(self):
        if (self.ear_punch is not None) or (self.ear_punch != 'none'):
            tmp = utils.select('Choose ear punch type: ', ['L', 'R', 'LR', 'LL', 'RR'])
            conn = server.connect_server()
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE surg_info
                SET ear_punch = '{}'
                WHERE animalid = '{}'
                """.format(tmp, self.animalid)
            )
            conn.commit()
            conn.close()
        else:
            print('This animal has been punched before.')
