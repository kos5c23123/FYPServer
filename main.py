import json
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
import time

cred = credentials.Certificate("assets/firebaseKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://ouhk-fyp-375a7.firebaseio.com/'
})
#本港地區天氣報告
rhrread = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread"
#九天天氣預報
fnd = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd"

def CheckTime():
    NowHour = datetime.today().strftime('%H')
    NowSec = datetime.today().strftime('%S')
    NowMinute = datetime.today().strftime('%M')
    print(NowHour + ":" + NowMinute + ":" + NowSec)
    time.sleep(1)
    if NowSec == '00':
        if NowMinute == '00' or NowMinute == '30':
            GetWeather()
            GetFuture()
    if NowHour == '00' and NowMinute == '00' and NowSec == '00':
        GetSun()

def GetWeather():
    print("GetWeather:Start to send data to firebase!")
    NowDay = datetime.today().strftime('%Y-%m-%d')
    NowHour = datetime.today().strftime('%H')
    NowMinute = datetime.today().strftime('%M')
    NowMinAndSec = (NowHour + ":" + NowMinute)  
    req = requests.get(rhrread)
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
    print("GetWeather:Finished Sending!")

def GetFuture():
    print("GetFuture:Start to send data to firebase!")
    req = requests.get(fnd)
    req_json = json.loads(req.text)
    futureWeather = req_json['weatherForecast']
    # ref = db.reference('/HK').child('Next7Days')
    DateArray = []
    for x in range(len(futureWeather)):
        DateArray.append(str(x))
        ref = db.reference('/HK').child('Next7Days').child(DateArray[x])
        ref.set({
            'Date' : futureWeather[x]['forecastDate'],
            'MaxTemp' : futureWeather[x]['forecastMaxtemp']['value'],
            'MinTemp' : futureWeather[x]['forecastMintemp']['value'],
            'icon' : futureWeather[x]['ForecastIcon']
        })
    print("GetFuture:Finished Sending!")

def GetSun():
    print("GetSun:Start to send data to firebase!")
    Year = datetime.today().strftime('%Y')
    Month = datetime.today().strftime('%m')
    Day = datetime.today().strftime('%d')
    #日落日出
    SRS = "https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=SRS&year=" + Year + "&month=" + Month + "&day=" + Day + "&rformat=json"
    req = requests.get(SRS)
    req_json = json.loads(req.text)
    Sun = req_json['data']
    NowDay = datetime.today().strftime('%Y-%m-%d')
    ref = db.reference('/HK').child(NowDay)
    for x in range(len(Sun)):
        ref.set({
            'Up' : Sun[x][1],
            'down' : Sun[x][3]
        })
    print("GetSun:Finished Sending!")

while True:
    CheckTime()
