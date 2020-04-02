import config
import func
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
from datetime import time, date, datetime
import mysql.connector
import time
import schedule
import shedule_functions

user_dict = {}

bot = telebot.TeleBot(config.TOKEN)

udb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd = config.passwd,
    database = "users"
)

u_cursor = udb.cursor()

class User:
    def __init__(self, id, name):
        self.name = name
        self.chatID = id
        self.location = None
        self.startTime = None
        self.notification = 1
        self.shedule = None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        chat_id = message.chat.id
        name = message.from_user.first_name
        user = User(chat_id,name)
        if chat_id not in user_dict:
            user_dict[chat_id] = user
            bot.send_message(chat_id, "Hello, stranger, let me scan you...")
            bot.send_message(chat_id, "Scanning complete, I know you now")
            command_help(message)
        else:
            bot.send_message(chat_id, "I already know you, "+ user.name + ",no need for me to scan you again!")

    except Exception as e:
        bot.reply_to(message, 'Sorry, bad connection')

@bot.message_handler(commands=['help'])
def command_help(message):
    chat_id  = message.chat.id
    help_text = "The following commands are available: \n"
    commands = func.commands
    for key in commands:
        help_text += "/" + key + ":"
        help_text += commands[key] + "\n"
    bot.send_message(chat_id , help_text)

@bot.message_handler(commands=['setlocation'])
def cmd_setLocation(message):
    chat_id  = message.chat.id
    response = bot.reply_to(message, 'Please, set the desired location')
    bot.register_next_step_handler(response, set_loc)

def set_loc(message):
    chat_id = message.chat.id
    location = message.text
    response = func.check_place(location)
    if response == True :
        user = user_dict[chat_id]
        user.location = location
        bot.send_message(chat_id, "Okay, your location is "+ user.location)
        check_UUI = func.check_id(chat_id, u_cursor)
        if check_UUI == False:
            sql = "UPDATE users_data SET location = %s WHERE ID = %s"
            val = (str(location), str(chat_id))
            u_cursor.execute(sql, val)
            udb.commit()

    elif response == False :
        bot.send_message(chat_id, " It\'s wrong location.\nPlease, try again by command \'/setlocation\' ~.")

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

@bot.message_handler(commands=['setnotificationshedule'])
def shedule(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("12", callback_data="12"),
                InlineKeyboardButton("24",callback_data="24"),
                InlineKeyboardButton("36",callback_data="36"),
                InlineKeyboardButton("48", callback_data="48"))
    bot.send_message(message.chat.id, "Please, set wished shedule", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    user = user_dict[chat_id]
    user.shedule = call.data
    bot.send_message(call.message.chat.id, "Okay, you are set "+ user.shedule)
    check_UUI = func.check_id(chat_id, u_cursor)
    if check_UUI == False:
        sql = "UPDATE users_data SET shedule = {0} WHERE ID = {1}".format(user.shedule, user.chatID)
        u_cursor.execute(sql)
        udb.commit()

@bot.message_handler(commands=['enablenotification'])
def cmd_enableNotification(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if user.location is None :
        bot.send_message(chat_id,'Sorry, I can\'t enable notification, because I don\'t know your location ~')
        bot.send_message(chat_id, 'You can set your location by command \'/setlocation\' ~')
    elif user.shedule is None :
        bot.send_message(chat_id,'Sorry, I can\'t enable notification, because you are don\'t set notification shedule ~')
        bot.send_message(chat_id, 'You can set your location by command \'/setnotificationshedule \' ~')
    else :
        user.startTime = datetime.now()
        user.notification = 0
        bot.send_message(chat_id, 'You are just activate me !!!')

        if user.notification == 0 :
            notif = "ON"
        bot.send_message(chat_id, '\nYou are '+ user.name + ' \nYour location is '+ user.location+ '\nStart time: '+ str(user.startTime) + '\nNotifications : '+ notif + '\nShedule :'+ str(user.shedule))

        sql = "SELECT * FROM users_data WHERE ID = {0}".format(chat_id)
        u_cursor.execute(sql)
        existsUser = u_cursor.fetchone()

        check_UUI = func.check_id(chat_id, u_cursor)
        if check_UUI == True:
            sql = "INSERT INTO users_data (ID, name, location, start, notification, shedule) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (str(user.chatID), str(user.name), str(user.location), str(user.startTime), str(user.notification), str(user.shedule))
            u_cursor.execute(sql, val)
            udb.commit()

            shedule_functions.response(chat_id, True, u_cursor, bot)

        else :
            sql = "UPDATE users_data SET notification = {0} WHERE ID = {1}".format(user.notification, user.chatID)
            u_cursor.execute(sql)
            udb.commit()

            shedule_functions.response(chat_id, True, u_cursor, bot)

@bot.message_handler(commands=['disablenotification'])
def cmd_disableNotification(message):
        chat_id = message.chat.id
        user = user_dict[chat_id]
        if user.notification == 1:
            bot.send_message(chat_id, 'Notifications are disabled')
        else :
            user.startTime = None
            user.notification = 1
            sql = "UPDATE users_data SET notification = %s WHERE ID = %s"
            val = (str(user.notification), str(chat_id))
            u_cursor.execute(sql, val)
            udb.commit()
            bot.send_message(chat_id, 'Okay, notifications are disabled')

            shedule_functions.response(chat_id, False, u_cursor, bot)

@bot.message_handler(commands=['getweather'])
def getWeather(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if user.location == None :
        bot.send_message(chat_id, 'For getting current weather you need to set wished location by command \'/setlocation\' ')
    else :

        bot.send_message(chat_id,func.get_weather(user.location))

#only for breaking
@bot.message_handler(func=lambda message: message.text == "stop")
def stop(message):
    user = Us_er(chat_id,name)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    bot.send_message(m.chat.id, "Sorry, I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")

bot.polling()
