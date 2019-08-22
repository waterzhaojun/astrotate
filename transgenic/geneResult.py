import pandas as pd
import os
import psycopg2
import argparse
import util

if __name__ == "__main__":
    resultfolder = util.get_config()['gene_test_result_folder']
    company = util.get_config()['gene_test_company']
    conn = util.connect_server()
    files = [x for x in os.listdir(resultfolder) if x.startswith('OrderResults-') and x[-4:] == '.csv']
    if len(files) != 1:
        raise Exception('Please confirm there is result file in the folder %s' % resultfolder)
    else:
        resultfile = os.path.join(resultfolder, files[0])
    
    df = pd.read_csv(resultfile)

    plate = df.loc[0, 'WellPlate']
    
    
    columns = list(df.columns)
    sbar = columns.index('TranslatedResult')
    for i in range(len(df)):

        # update gene information. If you want to change gene information format, please edit below code.===========================
        gene = ''
        for j in range(sbar+1, len(columns)):
            gene = gene+ columns[j] + '(' + df.iloc[i,j].replace(' ', '') + ')'
            if j <len(columns)-1:
                gene = gene + ' '
        
        # get animal feature =======================================================================================================
        tmp = df.loc[i, 'Sample']
        cageid = 'C%03d' % int(tmp.split('-')[-2][1:])
        ear_punch = tmp.split('-')[-1]
        
        # start to update gene information =========================================================================================
        cur = conn.cursor()
        cur.execute(
        """
        update transgenic_animal_log
        set genotype='{}', plate_num='{}', test_company='{}'
        where cageid='{}' and ear_punch='{}'
        """.format(gene, plate, company, cageid, ear_punch)
        )
        conn.commit()

        print("%s %s's gene is %s" % (cageid, ear_punch, gene))

    os.remove(resultfile)
