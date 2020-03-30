import schedule
import func
import time
from datetime import datetime


def response(chat_id, res, cursor, bot):
    schedule.clear()

    tuple_data = ()
    cursor.execute("SELECT * FROM users_data WHERE ID = {0}".format(chat_id))
    tuple_data = cursor.fetchone()
    def send_weater(chat_id):
        response = func.get_weather(tuple_data[2])
        bot.send_message(chat_id, response)

    schedule.cancel_job(send_weater)

    if res == True:
        schedule.every(tuple_data[5]).minutes.do(send_weater,chat_id)
        while True:
            schedule.run_pending()
            time.sleep(1)
        bot.send_message(chat_id, "Start")

    elif res == False:
        bot.send_message(chat_id, "Clear")
