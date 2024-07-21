#telegram bot for moderation groups
#bot name:  sahbot
#bot username: mupsah_bot


import telebot
import re
import json
from datetime import datetime, timedelta
from telebot import types
from telebot.util import update_types
from pprint import pprint # to investigate what inside objects
import sqlhelper2


f = open("token.txt","r")
token = f.readline()
token = token.rstrip() # read about function
print(token, type(token))
f.close()
bot = telebot.TeleBot(token, parse_mode=None)

#TODO it only get users on Python script starts. If new grup added without restart futher functionts don't see them
#   think about move it for more often renewal of new users and groups(chats)
#   maby compare day number at start and in message and refresh if it changes?
global tid_list
tid_list = sqlhelper2.db_get_users() # tg id of all users in chat(s)

superadmins = ('detoxicon')

print('- - - get users id from DB - - -')
print(list(tid_list))

global chat_list_refresh_date
global chat_list
chat_list_refresh_date = datetime.now().date()
chat_list = sqlhelper2.db_get_chats()
print('- - - get chats - - -')
print(list(chat_list))

#print('- - - trying ban - - -')
#bot.ban_chat_member(-1002085056136,775803031,60,True)

print(bot.get_me())
print(types.BotCommandScope)
#print(bot.get_chat('@tbros'))
#bot.send_message('@tbros','aaa')

bc_block_user = types.BotCommand('block_user','заблокировать пользователя')
bc_a = types.BotCommand('fun','anekdot')
bc_q = types.BotCommand('question','ask smt')
bot.set_my_commands([bc_block_user,bc_a,bc_q])
#bot.set_my_commands([bc,bc_a,bc_q], types.BotCommandScope())


#types.MenuButtonDefault('default')

# try send message to user

# functions for multiple usage 

def check_tables(message):
    print('- - - check_tables - - - ')
    print(message.from_user.username)
    tid = message.from_user.id
    vname = message.from_user.username
    fname = message.from_user.first_name
    lname = message.from_user.last_name
    vtext = message.text

    # check for user in DB and write if not
    global tid_list
    if tid not in tid_list:
        sqlhelper2.db_new_user(tid,vname,fname,lname)
        tid_list = sqlhelper2.db_get_users()
    else:
        print('user already in DB')

    # every next day refresh chat list
    global chat_list_refresh_date
    if chat_list_refresh_date < datetime.now().date():
        chat_list_refresh_date = datetime.now().date()

    print(f'- - - - chat_list_refresh_date: {chat_list_refresh_date}')

    # check for new group or chat and write it to DB if it not saved yet
    global chat_list
    chat_id = message.chat.id
    
    if chat_id not in chat_list:
        chat_title = message.chat.title
        sqlhelper2.db_new_chat(chat_id, chat_title)
        chat_list = sqlhelper2.db_get_chats()
    else:
        print('chat already known id DB')

#commands
@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.reply_to(message, "\U0001F916Добро пожаловать!")
    print('bot.message.form_user.id: '+ str(message.from_user.id))
    print('bot.message.form_user.id: '+ str(message.from_user.id))
    #start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    #start_markup.row('/start', '/help', '/hide')

# try handle when new member comes to group
print(' = = = = =  member update handler = = = = = =')
print('_')
@bot.message_handler(content_types=["new_chat_members"])
def new_member_comes(updated):
    print('there is new member --> ')
    print('-end of member fucn -')
    #telebot.types.ChatMemberUpdated

# = = = = = = = = = = = = =  Manual block user command = = = = = = = = = = = = = 

@bot.message_handler(commands=['block_user'])
def send_welcome(message):
    #TODO add checking if request only from superadmin
    if message.from_user.username in superadmins:
        bot.send_message(message.chat.id, "\U0001F916 Будем плокировать! Кого? Введите ник либо ")
        print('= = = = = Block user mode = = = = = ')
        print(list(tid_list))
        bot.register_next_step_handler(message, ask_username_to_block)
        #sqlhelper2.db_get_user(tid_list[1])
        #start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        #start_markup.row('/start', '/help', '/hide')
    else:
        bot.reply_to(message, "You have no right to do this." )

def ask_username_to_block(message):
    founded_user = sqlhelper2.db_get_user(message.text)
    if founded_user is None:
        bot.send_message(message.chat.id, "Sorry can't find user with simmilar name.")
    else:
        print(list(founded_user))
        bot.send_message(message.chat.id, founded_user[1] + '. Do you really want to ban him? + if Yes')
        found_tid = founded_user[0]
        bot.register_next_step_handler(message,ask_confirm_ban, found_tid)
        

def ask_confirm_ban(message, tid):
    if message.text == '+':
        for ch in chat_list:
            print(f' - - - - - BANNED! in {ch}')
        print(tid)
    else:
        print('user banning canceld ' + str(tid) + ' message was: ' + message.text)

#

@bot.message_handler(regexp=".*(хуй|пизд|сука|ебан|алуп|чмо|fu|еблан|пид(о|а)|п(p|р)(о|o)д(а|a)|изготови|insta|hats|elegr).*")
def echo_rex(message):
    #bot.send_message(message.chat.id, "Не ругайся!")
    #bot.reply_to(message,"ответ наругань")
    print( message.chat.__dir__())
    print(' - - - - -  chat __dict__ - - - - -  ')
    print( message.chat.__dict__)

    print(' ==== PG request - checking and adding violation to DB ==== ')
    tid = message.from_user.id
    vname = message.from_user.username
    fname = message.from_user.first_name
    lname = message.from_user.last_name
    vtext = message.text

    # check if user tid and group id saved in DB
    check_tables(message)

    vcounter = sqlhelper2.db_add_violation(tid,vname,vtext)
    print(' Your have '+str(vcounter) + '/3 violations')
    print(' - - - - -  from_user __dict__ - - - - -  \n')
    print(message.from_user.__dict__)
    
    #print( bot.get_сhat(message.chat.id)) # 'TeleBot' object has no attribute 'get_сhat'
    print('--- chat.permissions ---')
    print(message.chat.permissions)
    ban_days = 0
    ban_hours = 0 #
    ban_minutes = 3
    unban_time = datetime.now() + timedelta(hours=ban_hours, minutes=ban_minutes)
    unban_time_pretty = unban_time.strftime('%Y.%m.%d %H:%M')

    new_perm = types.ChatPermissions(can_send_messages=False)
    print('- New permission -')
    print(new_perm)
    #can't restrict chat owner
    if vcounter == 3 and vname != 'detoxicon':
        bot.reply_to(message,'У вас '+str(vcounter) + 'из 3 нарушений. Бан до ' + unban_time_pretty)
        bot.restrict_chat_member(message.chat.id, message.from_user.id, unban_time)
        sqlhelper2.db_violation_threshold(tid)
    else:
        if vname == 'detoxicon' and vcounter ==3:
            bot.reply_to(message,f'''У вас {vcounter} из 3 нарушений. Но вам можно!
Время бана составляет: {ban_hours} часов и {ban_minutes} минут. Test time: {unban_time_pretty}''')
            sqlhelper2.db_violation_threshold(tid)
        else:
            bot.reply_to(message,'У вас '+str(vcounter) + ' из 3 нарушений. При достижении бан!')
    print("user id:" + str(message.from_user.id))
    #bot.reply_to(message, '''Вы хотите зарегистрировать ЛК!''')

@bot.message_handler(regexp=".*топи.*")
def echo_rex(message):
    bot.reply_to(message, '''Вы хотите узнать ЛС!''')

#regexp example 3
@bot.message_handler(regexp=".*(рикрепи|обавить).*")
def attach_ls(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('send shit'))
    msg = bot.send_message(message.chat.id, "choose type shit", reply_markup=markup)
    

#anything other messages
@bot.message_handler(func=lambda m:True)
def echo_all(message):
    print('---------- ANYTHING -----------')
    check_tables(message)

bot.infinity_polling()

