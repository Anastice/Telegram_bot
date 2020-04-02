import pyowm
import config
from datetime import datetime


commands = {
    "start ":" Get used to the bot",
    "help ": "Gives you information about the available commands",
    "setlocation":" Sets the desired location",
    "setnotificationshedule ":" Gives you options for the time period after which you will be notified",
    "enablenotification ":" Activates notification",
    "disablenotification ":" Deactivates notification",
    "getweather ":" Show the weather forecast in the desired location right now"
}

def check_place(place):
    try:
        owm = pyowm.OWM(config.owm)
        observation = owm.weather_at_place(place)
        response = True
    except  Exception as e:
        response = False
    return response

def check_id(id, cursor):
    sql = "SELECT * FROM users_data WHERE ID = {0}".format(id)
    cursor.execute(sql)
    existsUser = cursor.fetchone()
    if existsUser is None:
        new = True
    else:
        new = False
    return new

def get_weather(place):
    owm = pyowm.OWM(config.owm)
    observation = owm.weather_at_place(place)
    w = observation.get_weather()

    temp = w.get_temperature('celsius') ["temp"]
    response = "Now " + str(datetime.now()) +"\nIn " + place + " the weater is " + w.get_detailed_status() + "\nAnd the temperature : " + str(temp)

    return response
