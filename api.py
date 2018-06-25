from bs4 import BeautifulSoup
import requests
import json
import collections
import datetime

def getStationFromTrainNumber(trainNo, jDate=datetime.date.today().strftime('%d-%b-%Y'),jDateDay=str(datetime.date.today().strftime('%A')[:3]).upper()):
    data = {'trainNo': trainNo, 'jDate': jDate, 'jDateMap': jDate, 'jDateDay': jDateDay}
    stationsList = collections.OrderedDict()
    r = requests.post('https://enquiry.indianrail.gov.in/mntes/q?opt=TrainRunning&subOpt=FindStationList', data=data)
    soup = BeautifulSoup(r.text, 'lxml')
    stations = soup.find(id='jStation').find_all('option')[1:]
    for station in stations:
        stationsList[station.get('value')] = station.text
    finaldata = {}
    finaldata['stations'] = stationsList
    finaldata['originalReq'] = data
    return json.dumps(finaldata)


def TrainRunningStatus(trainNo, jStation, jDate=datetime.date.today().strftime('%d-%b-%Y'),
                       jDateMap=datetime.date.today().strftime('%d-%b-%Y'),
                       jDateDay=str(datetime.date.today().strftime('%A')[:3]).upper()):
    data = {'trainNo': trainNo, 'jStation': jStation, 'jDate': jDate, 'jDateMap': jDate, 'jDateDay': jDateDay}
    r = requests.post('https://enquiry.indianrail.gov.in/mntes/q?opt=TrainRunning&subOpt=ShowRunC', data=data)
    soup = BeautifulSoup(r.text, 'lxml')
    resultData = {}
    try:
        table = soup.find(id='ResTab')
        trs = table.find_all('tr')
        trainName = trs[0].find_all('td')[1].text
        stationName = trs[1].find_all('td')[1].text
        schArTime = trs[3].find_all('td')[1].text
        actArTime = trs[4].find_all('td')[1].text
        delayTime = trs[5].find_all('td')[1].text
        lastLocation = (trs[9].find_all('td')[1].text)
        lastLocation = " ".join(lastLocation.split())
        resultData = {'trainName': trainName, 'schArTime': schArTime, 'actArTime': actArTime, 'delayTime': delayTime,
                      'lastLocation': lastLocation, 'stationName': stationName}
    except:
        # err = soup.find_all(class_='errorTextL11')[0].text
        resultData['err'] = 'Either the Train Number' + str(
            trainNo) + " does\'t run on " + jDateDay + " at " + jStation[
                                                                :3] + " Station or the train number is incorrect"
    return resultData


def getStationNamesforliveStation(fbid, stationFrom, stationTo, type):
    err = 0
    if type == 1:
        getStationFromList = [station for station in LiveStationList if stationFrom.upper() in station]
        btnarr = []
        if len(getStationFromList) > 0:
            isinit = 1
            for station in getStationFromList:
                btnarr.append({"type": "postback", "title": station, "payload": json.dumps(
                    {"PBRType": "livestation", "validStationFrom": station, "stationTo": stationTo})})
            morestations = split(btnarr, 3)
            for buttons in morestations:
                if isinit:
                    data = {"text": "Select any one Source Station ", "Buttons": buttons}
                    isinit = 0
                else:
                    data = {"text": "Or Select from these Similar Station Name", "Buttons": buttons}
                post_facebook_buttons(fbid, data)
        else:
            post_facebook_message_normal(fbid, "No Station Found named " + stationFrom + ". Try spelling it correctly")
    elif type == 2:
        cnfStation = stationFrom
        getStationToList = [station for station in LiveStationList if stationTo.upper() in station]
        btnarr = []
        if len(getStationToList) > 0:
            isinit = 1
            for station in getStationToList:
                btnarr.append({"type": "postback", "title": station, "payload": json.dumps(
                    {"PBRType": "livestation", "validStationFrom": cnfStation, "validStationTo": station})})
            morestations = split(btnarr, 3)
            for buttons in morestations:
                if isinit:
                    data = {"text": "Select any one Destination Station  ", "Buttons": buttons}
                    isinit = 0
                else:
                    data = {"text": "or Select from these similar station name  ", "Buttons": buttons}
                post_facebook_buttons(fbid, data)
        else:
            post_facebook_message_normal(fbid, "No Station Found named " + stationFrom + ". Try spelling it correctly")


def getLiveStation(fbid, stationFrom, stationTo):
    url = 'https://enquiry.indianrail.gov.in/mntes/q?opt=LiveStation&subOpt=show'
    data = 'jFromStationInput=' + stationFrom + '&jToStationInput=' + stationTo + '&nHr=4&jStnName=&jStation='
    r = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=data)
    soup = BeautifulSoup(r.text, 'lxml')
    try:
        trs = soup.find('tbody').find_all('tr')
        post_facebook_message_normal(fbid, "There are " + str(
            len(trs) - 2) + " trains in next 4 hours between " + stationFrom + " and " + stationTo)
        for i in range(2, len(trs)):
            trainName = trs[i].find_all('td')[0].text
            trainArr, trainDep = (trs[i].find_all('td')[1].text).split()
            atrainArr, atrainDep = (trs[i].find_all('td')[2].text).split()
            platform = trs[i].find_all('td')[3].text
            rsData = {"recipient": {"id": fbid}, "message": {"attachment": {"type": "template",
                                                                            "payload": {"template_type": "generic",
                                                                                        "elements": [{
                                                                                                         "title": trainName + " will Arrive at " + atrainArr + " on platform number " + platform,
                                                                                                         "image_url": "",
                                                                                                         "subtitle": "Sample"}]}}}}
            status = requests.post(page_url_with_token, headers={"Content-Type": "application/json"},
                                   data=json.dumps(rsData))
            print status.json()
    except:
        try:
            err = soup.find_all(class_='errorTextL11')[0]
            post_facebook_message_normal(fbid, err.text)
        except:
            post_facebook_message_normal(fbid, "Server Error please try after some time")
