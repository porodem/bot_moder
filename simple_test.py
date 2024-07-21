# test postgres for moder bot

import sqlhelper
import datetime
import re


print('- start test sql -')
print()

advRegex = re.compile(r'.*(п(р|p)(o|о)да|изгот).*',re.I)
re_test=advRegex.search('Прoдам сало')
if re_test is not None:
    print('Found - - - - - - - - - - : ' + re_test.group())

print('end regex')


def call_doc():
    print('call_doc')
    doc_comming()

def doc_comming():
    print('doc_comming')

call_doc()

# chat_list_refresh_date = datetime.datetime.now().date()
# td = chat_list_refresh_date + datetime.timedelta(hours=1, minutes=1)
# print(f'chat refresh {chat_list_refresh_date} and delta {td}', chat_list_refresh_date < td)

#tid_list = sqlhelper2.db_get_users()
#print('We got list of users id: ' + str(list(tid_list)))

#result = sqlhelper.db_check_violations(775803031)

# if result:
#     print('user exists')
# else:
#     print('not exists: result is ' + str(result)) 


print()

print(datetime.datetime.now().strftime('%m/%d/%Y %H:%M'))

print(' - end - ')
