"""
This module is to transfer database tables to csv files. 
Based on the table structure, and the target csv files requires, we use different function for different table.
"""

import server

def transfer_ihc_info():
    conn = server.connect_server()
    cur = conn.cursor()
    cur.execute(
    """
    select * from ihc_info
    """
    )
    res = cur.fetchall()
    conn.commit()

    conn.close()
    return(res)