import json
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
import time

cred = credentials.Certificate("firebaseKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://ouhk-fyp-375a7.firebaseio.com/'
})

URL = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread"

def CheckTime():
    NowHour = datetime.today().strftime('%H')
    NowSec = datetime.today().strftime('%S')
    NowMinute = datetime.today().strftime('%M')
    print(NowHour + ":" + NowMinute + ":" + NowSec)
    time.sleep(1)
    if NowSec == '00':
        if NowMinute == '00' or NowMinute == '30':
            GetData()


def GetData():
    print("start to send data to firebase!")
    NowDay = datetime.today().strftime('%Y-%m-%d')
    NowHour = datetime.today().strftime('%H')
    NowMinute = datetime.today().strftime('%M')
    NowMinAndSec = (NowHour + ":" + NowMinute)  
    req = requests.get(URL)
    req_json = json.loads(req.text)
    Temp = req_json['temperature']['data']
    Rain = req_json['rainfall']['data']
    ref = db.reference('/HK').child(NowDay).child(NowMinAndSec)
    if req_json['uvindex'] == "":
        ref.set({
        'icon' : req_json['icon'],
        'UV' : 0,
        'humidity' : req_json['humidity']['data'][0]['value']
    })
    else:
        ref.set({
        'icon' : req_json['icon'],
        'UV' : req_json['uvindex']['data'][0]['value'],
        'humidity' : req_json['humidity']['data'][0]['value']
    })
    for x in range(len(Temp)):
        ref.child('direct').child(Temp[x]['place']).set({
            'temperature' : Temp[x]['value']
        })
    for x in range(len(Rain)):
        if (len(Rain[x]) == 5):
            ref.child('rainfall').child(Rain[x]['place']).set({
            'main' :Rain[x]['main'],
            'max' : Rain[x]['max'],
            'min' : Rain[x]['min']
            })
        elif (len(Rain[x]) == 4):
            ref.child('rainfall').child(Rain[x]['place']).set({
            'main' :Rain[x]['main'],
            'max' : Rain[x]['max']
            })
    print("Finished Sending!")

while True:
    CheckTime()