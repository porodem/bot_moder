# test postgres for MODERATOR BOT

import psycopg

def db_check_violations(args):
    
    tid = args
    user_exist = False

    q = '''select * from violations v
    where telegram_id = %s
    '''

    with psycopg.connect('dbname=chat user=bering_bot host=localhost password=bering') as conn:
        with conn.cursor() as cur:
            cur.execute(q,(tid,))
            #cur.execute(q,(p_id,))
            b = cur.fetchall()
            cnt = cur.description
            print(cnt[0].name)
            for record in b:
                rrec = str(record[1]) + record[3]
                print('rrec: ' + rrec)
                user_exist = True
            conn.commit()
    return user_exist


def db_add_violation():

    q = '''INSERT INTO violations(tname) VALUES(%s);'''
