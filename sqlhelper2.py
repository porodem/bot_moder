# test postgres for MODERATOR BOT

import psycopg
from datetime import datetime, timedelta

con = psycopg.connect('dbname=chat user=bering_bot host=localhost password=bering')

violations_limit = 3
current_violations = 0
invite_date = None

def db_get_users():
     print('-- get all users --')
     q = 'select telegram_id from tg_users'
     tid_list = []

     with con.cursor() as cur:
          cur.execute(q)
          b = cur.fetchall()
          print(type(b))
          print(list(b))
          for record in b:
               tid_list.append(record[0])
               
     return tid_list

def db_new_user(tid,username,fname = "",lname=""):
     print(' - Write new user to DB - - -')
     q = '''INSERT INTO tg_users(telegram_id, invite_date, username, first_name, last_name) VALUES(%s, current_date, %s,%s,%s);'''
     cur = con.cursor()
     cur.execute(q,(tid,username,fname,lname))
     con.commit()

def db_get_user(username):
     print(' - - - - - get specific user - - - - -')
     print(username)
     q = '''SELECT telegram_id, username, first_name, last_name, invite_date FROM tg_users WHERE username ~* %s '''
     cur = con.cursor()
     cur.execute(q,(username,))
     b = cur.fetchone()
     if b is None:
          result = None
     else:
          print(b[0])
          print(f'User {b[1]} with telegram id: {b[0]}')
          result = b
          print('===== CONVERSION: ')
          print(result)

     return result

def db_get_chats():
     print('-- get all users --')
     q = 'select chat_id from chats'
     chat_list = []

     with con.cursor() as cur:
          cur.execute(q)
          b = cur.fetchall()
          for record in b:
               chat_list.append(record[0])
     return chat_list

def db_new_chat(chat_id, title):
     print(' - - - write new group - - -')
     q = '''INSERT INTO chats(chat_id, title) VALUES(%s,%s)'''
     cur = con.cursor()
     cur.execute(q,(chat_id,title))

# - - - - -  V I O L A T I O N S  - - - - - 

def db_check_violations(args):
    print('checking violation ')
    global current_violations
    global invite_date
    current_violations = 0
    tid = args
    #user_exist = False

    q = '''select * from violations v
    where telegram_id = %s
    '''

    q2 = '''select vcounter, invite_date from tg_users tu 
    left join violations v on tu.telegram_id = v.telegram_id    
    where tu.telegram_id = %s
    '''


    with con.cursor() as cur:
            cur.execute(q2,(tid,))
            #cur.execute(q,(p_id,))
            b = cur.fetchone() #fetchall()
            cnt = cur.description
            print('Show 1st field:',cnt[0].name)
            #for record in b:
            #    print(record[1],record[3])
            if b[0] is None:
                return -1
            current_violations = b[0]
            invite_date = b[1]
            safe_member_period = datetime.now().date() - timedelta(days=1)
            if invite_date > safe_member_period:
                 print('- - - - - - Too early violation happend: ' + str(safe_member_period))
                 # TODO warning msg to member and ban him
                 # TODO count total msges of member
            #user_exist = True
            print('query gets ',b)

    con.commit()

    print('func return counter :', current_violations)
            
    return current_violations


def db_add_violation(tid, vname, vtext):
    global current_violations
    v = db_check_violations(tid)
    print('add violation for: ',tid,vname,vtext)

    db_hist_write(tid,vtext)

    if v != -1:
        print(' - violations plus - ')
        db_plus_violation(tid)        
    else:        
        q = '''INSERT INTO violations(telegram_id,tname,vdate,last_v_text,vcounter) VALUES(%s,%s, now(),%s,1);'''

        cur = con.cursor()
        cur.execute(q,(tid,vname,vtext))

        con.commit()

    return current_violations + 1


def db_plus_violation(tid):
    q = '''update violations set vcounter = vcounter + 1 where telegram_id = %s;'''
    
    cur = con.cursor()
    cur.execute(q,(tid,))
    con.commit()
    print('violation has been increased')

def db_violation_threshold(tid):
    q = '''update violations set vcounter = 0, ban_counter = ban_counter + 1 where telegram_id = %s;'''
    
    cur = con.cursor()
    cur.execute(q,(tid,))
    con.commit()
    print('ban_counter has been increased')

def db_hist_write(tid, vtext):
    print('- writing history -')
    q ='''INSERT INTO violations_hist(telegram_id, vdate, vtext) VALUES(%s, now(), %s);'''
    cur = con.cursor()
    cur.execute(q,(tid,vtext,))
