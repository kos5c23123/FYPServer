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
#本港地區天氣報告
rhrread = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread"
#天氣警告資訊
warningInfo = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo"
#天文台XML
hkourl = "http://www.hko.gov.hk/wxinfo/json/one_json.xml"

def Timer():
    NowHour = datetime.today().strftime('%H')
    NowSec = datetime.today().strftime('%S')
    NowMinute = datetime.today().strftime('%M')
    print(NowHour + ":" + NowMinute + ":" + NowSec)
    time.sleep(1)
    if NowSec == '00':
        if NowMinute == '00' or NowMinute == '30':
            GetWeather()

def GetWeather():
    print("GetWeather:Start to send data to firebase!")
    NowDay = datetime.today().strftime('%Y-%m-%d')
    NowHour = datetime.today().strftime('%H')
    NowMinute = datetime.today().strftime('%M')
    NowMinAndSec = (NowHour + ":" + NowMinute)
    hkoAPI_Data = requests.get(rhrread).json()
    hkodata = requests.get(hkourl).json()
    Temp = hkoAPI_Data['temperature']['data']
    Rain = hkoAPI_Data['rainfall']['data']
    ref2 = db.reference('/HK').child(NowDay)
    ref = db.reference('/HK').child(NowDay).child(NowMinAndSec)
    if hkoAPI_Data['uvindex'] == "":
        ref.set({
        'icon' : hkoAPI_Data['icon'],
        'UV' : 0,
        'humidity' : hkoAPI_Data['humidity']['data'][0]['value']
    })
    else:
        ref.set({
        'icon' : hkoAPI_Data['icon'],
        'UV' : hkoAPI_Data['uvindex']['data'][0]['value'],
        'humidity' : hkoAPI_Data['humidity']['data'][0]['value']
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
    ref2.update({
        "HighTemp" : hkodata['hko']['HomeMaxTemperature'],
        "LowTemp" : hkodata['hko']['HomeMinTemperature']
    })
    print("GetWeather:Finished Sending!")
    
while True:
    Timer()

# reqwarninfo = requests.get(warningInfo).json()
# warnStatusCode = []
# if (reqwarninfo == {}):
#     print("Yes")
# else:
#     warninfo = reqwarninfo['details']
#     for x in range(len(warninfo)):
#         warnStatusCode.append(warninfo[x]['warningStatementCode'])