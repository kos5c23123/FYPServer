import json
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
import time

DayTimeArray = []
for x in range(24):
    DayTimeArray.append(x)
cred = credentials.Certificate("firebaseKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://ouhk-fyp-375a7.firebaseio.com/'
})
#本港地區天氣報告
rhrread = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread"
#九天天氣預報
fnd = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd"
#天氣警告資訊
warningInfo = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo"
#未來48小時預報
onecall = "https://api.openweathermap.org/data/2.5/onecall?lat=22.302711&lon=114.177216&%20exclude=hourly&appid=f6314d411a30b19cfa90cbff38eb503a&units=metric"
#天文台XML
hkourl = "http://www.hko.gov.hk/wxinfo/json/one_json.xml"

def CheckTime():
    NowHour = datetime.today().strftime('%H')
    NowSec = datetime.today().strftime('%S')
    NowMinute = datetime.today().strftime('%M')
    print(NowHour + ":" + NowMinute + ":" + NowSec)
    time.sleep(1)
    if NowHour == '00' and NowMinute == '00' and NowSec == '00':
        GetSun()
    if NowSec == '00':
        if NowMinute == '00' or NowMinute == '30':
            GetWeather()
            GetFuture()
            Get48Future()
    if NowSec == '00' and NowMinute == '00':
        getTotoalData()

def GetWeather():
    print("GetWeather:Start to send data to firebase!")
    NowDay = datetime.today().strftime('%Y-%m-%d')
    NowHour = datetime.today().strftime('%H')
    NowMinute = datetime.today().strftime('%M')
    NowMinAndSec = (NowHour + ":" + NowMinute)
    req_json = requests.get(rhrread).json()
    hkodata = requests.get(hkourl).json()
    Temp = req_json['temperature']['data']
    Rain = req_json['rainfall']['data']
    ref2 = db.reference('/HK').child(NowDay)
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
    ref2.update({
        "HighTemp" : hkodata['hko']['HomeMaxTemperature'],
        "LowTemp" : hkodata['hko']['HomeMinTemperature']
    })
    print("GetWeather:Finished Sending!")

def GetFuture():
    print("GetFuture:Start to send data to firebase!")
    req_json = requests.get(fnd).json()
    futureWeather = req_json['weatherForecast']
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
    req_json = requests.get(SRS).json()
    Sun = req_json['data']
    NowDay = datetime.today().strftime('%Y-%m-%d')
    ref = db.reference('/HK').child(NowDay)
    for x in range(len(Sun)):
        ref.set({
            'Up' : Sun[x][1],
            'down' : Sun[x][3]
        })
    ref.update({
        'TotalRainFall' : '0'
    })
    print("GetSun:Finished Sending!")

def Get48Future():
    print("Get48Future:Start to send data to firebase!")
    req_json = requests.get(onecall).json()
    NowHour = datetime.today().strftime('%H')
    IntNowHour = int(NowHour)
    Temp = req_json['hourly']
    DateArray = []
    for x in range(len(Temp)):
        DateArray.append(str(x))
        ref = db.reference('/HK').child('Next48Hours').child(DateArray[x])
        ref.update({
            'time' : DayTimeArray[(IntNowHour+1) % len(DayTimeArray)],
            "temp" : int(Temp[x]['temp'])
        })
        IntNowHour += 1
    print("Get48Future:Finished Sending!")

def getTotoalData():
    NowDay = datetime.today().strftime('%Y-%m-%d')
    NowHour = datetime.today().strftime('%H')
    NowMinute = datetime.today().strftime('%M')
    NowMinAndSec = (NowHour + ":" + NowMinute)
    ref2 = db.reference('/HK').child(NowDay)
    ref = db.reference('/HK').child(NowDay).child(NowMinAndSec)
    Total = 0
    snapshot2 = ref2.get()
    PassRain = int(snapshot2['TotalRainFall'])
    Total = PassRain
    snapshot = ref.get()
    for val in snapshot['rainfall']:
        RainMax = int(snapshot['rainfall'][val]['max'])
        Total += RainMax
    ref2.update({
        'TotalRainFall' : Total
    })
    
while True:
    CheckTime()

# reqwarninfo = requests.get(warningInfo).json()
# warnStatusCode = []
# if (reqwarninfo == {}):
#     print("Yes")
# else:
#     warninfo = reqwarninfo['details']
#     for x in range(len(warninfo)):
#         warnStatusCode.append(warninfo[x]['warningStatementCode'])