import pandas as pd
import json
import plotly.express as px
import urllib.request
import time
import os
from math import radians, cos, sin, asin, sqrt

# FUNCTIONS
def save_file(issPos):
    # establish current time (this will always be unique for file naming)
    now = int(time.time())

    path = os.getcwd()
    # check is a dir for the save filles exists, if so set file path to variable
    if os.path.isdir('{}/issSaveFiles'.format(path)):
        savePath = '{}/issSaveFiles'.format(path)
    else:
        # define the name of the directory to be created
        extPath = "{}/issSaveFiles".format(path)
        try:
            os.mkdir(extPath)
        except OSError:
            print ("\nEarth cannot be found :  %s failed\n" % path)
        else:
            print ("\nLanding site established beginning final approach : %s \n" % path)
            savePath = '{}/issSaveFiles'.format(path)

    # we now set the save path and unique file name
    filePath = '{}/plot_{}.json'.format(savePath, now)
    try:
        with open(filePath,"w") as myFile:
            prepSave = json.dumps(issPos, indent=4)
            # new info of IssPos now saved in json formate for later reading
            myFile.write(prepSave)
    except Exception as e:
        print('\nAltimeter failure - error in save_file : {}\n'.format(e))

# VARIABLES

def fileSelect():
    # in this function we want to offer the available files as selectable
    # we do not want the user to enter their own file name as this can cause issues
    livePath = os.getcwd()
    # set location of previously saved data files
    filePath = '{}/issSaveFiles'.format(livePath)
    # files will be a memorie object and not a list
    files = os.scandir(filePath)
    # here we define an emty list to capture file names that can be index for user selection
    fileOptions = []

    fileSel = True
    while fileSel:
        index = 0
        # we should be tuple unpacking here as such....
        # for index, eachfile in enumerate(files)
        # however this was already coded
        for eachFile in files:
            fileOptions.append(eachFile)
            # set easy to read and understand name for display perposes
            name = eachFile.name
            print('[{}] - {}'.format(index,name))
            index += 1
        try:
            op = int(input('--> : '))
            if op == 999:
                print('LAUNCH ABOURTED')
                fileSel = False
            elif op in range(0,index):
                # set user chosen file from indexed file list
                chosenFile = fileOptions[op]
                # open file and set issPos list with json infomation
                with open(chosenFile, 'r') as myFile:
                    issPos = json.load(myFile)
                    print('\nSystems are a go : file {} open'.format(chosenFile))
                    print('Please stand by...')
                    fileSel = False
                # send read data for plotting
                plotISS(issPos)
            else:
                print('\nWE HAVE A PROBLEM : only numbers in range may be entered')
        except Exception as e:
            print('\nWE HAVE A PROBLEM : in fileSel : {}'.format(e))

def reportInfo(issPos):

    # if the ISS travels further than half an orbit the formula I am using will calculate the speed in reverse
    # this can be rectified for more accurate results if we had access to heading or course data
    # my fix was to limit the speed calculation to the first 30 min of data insuring less than half an orbit
    count = len(issPos)
    if count > 60:
        last = 60
    else:
        last = -1

    lon1 = float(issPos[0]['longitude'])
    lat1 = float(issPos[0]['latitude'])
    lon2 = float(issPos[last]['longitude'])
    lat2 = float(issPos[last]['latitude'])
    time1 = issPos[0]['timestamp']
    time2 = issPos[last]['timestamp']
    time3 = issPos[-1]['timestamp']
    dTime = time2 - time1
    dTime2 = time3 - time1

    # haversince() formula was found on the internet to calculate distance
    # between too GPS points including the curvature of the earth(radius)
    distance = haversine(lon1, lat1, lon2, lat2)

    # speed is given by distance/time - our time is in sec so we multiply by 3600 to get to hours
    # now we have km/h value
    speed = distance / dTime * 3600
    speed = round(speed, 0)
    startDate = time.ctime(time1)
    endDate = time.ctime(time3)
    duration = dTime2 / 60

    print('\n--------------------')
    print('   FLIGHT SUMMARY   ')
    print('--------------------')
    print('LAUNCH DATE : {}'.format(startDate))
    print('LANDING DATE : {}'.format(endDate))
    print('FLIGHT DURATION : {} minutes'.format(duration))
    print('FLIGHT SPEED : {} km/h'.format(speed))


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def plotISS(issPos):

    reportInfo(issPos)

    df = pd.DataFrame(issPos)

    fig = px.scatter_geo(df, lat='latitude', lon='longitude')
    print('\nReady for launch...\n')
    input('Press Enter for Launch')
    fig.show()

def trackISS(userTime):
    # User supplied time limit tracking
    # We ping the API for a position every 30sec as a recommended limit by the documentation
    # hence we multiply user supplied time by 2
    tMinus = userTime * 2
    # define an empty list to capture the API responces
    issPos = []
    # the following comment can be used for a single ISS position ping, we looking for multiple positions
    # http://open-notify.org/Open-Notify-API/ISS-Location-Now/
    url = 'http://api.open-notify.org/iss-now.json'
    # track amount of ping requests issued with loctions(aquired)
    locations = 0
    getLocation = True
    # adding drama
    print('\nTracking ISS - We are go for launch!\n Please stand by...\n')

    while getLocation:
        # open the API url
        response = urllib.request.urlopen(url)
        # once url is set open the supplied json file and set information to a Dct
        issDct = json.loads(response.read())
        # formate Dct
        issDct['latitude'] = issDct['iss_position']['latitude']
        issDct['longitude'] = issDct['iss_position']['longitude']
        issDct.pop('message')
        issDct.pop('iss_position')
        # add formated results to our ISS position list
        issPos.append(issDct)
        # calculate time left for application to run
        reportTime = tMinus - locations
        reportTime2 = reportTime / 2
        locations += 1
        # if time left is a whole minute (no seconds)
        if (reportTime % 2) == 0: 
            print('Destination in T- {} minutes and counting'.format(reportTime2))
        # check if user set time limit has ended and close loop
        if locations > tMinus:
            getLocation = False
        else:
            # API ping interval is hard coded to 30 sec, we could programme for user to supply the interval if needed
            time.sleep(30)

    # pass the newly created list of Dct loctaions called issPos to a save_file()
    save_file(issPos)

# MAIN LOOP
usingMenu = True

while usingMenu:
    print('\n----------------')
    print('    ISS MENU')
    print('----------------')
    print('[1] - Start Data Recording')
    print('[2] - View stored data')
    print('[999] - EXIT')

    try:
        op = int(input('--> : '))
        if op == 999:
            usingMenu = False
            print('TO INFINITY AND BEYOND')
        elif op == 1:
            print('\nIt takes approxamatly 90min to complete an orbit of the earth')
            print('How long(in minutes) shall we track for?')
            try:
                userTime = int(input('--> : '))
                if userTime != '':
                    trackISS(userTime)
                else:
                    print('T- cannot be empty')
            except Exception as e:
                print('WE HAVE A PROBLEM : in op 1 : {}'.format(e))
        elif op == 2:
            fileSelect()
        else:
            print('WE HAVE A PROBLEM : only numbers may be used as options')
    except Exception as e:
        print('WE HAVE A PROBLEM : in usingMenu : {}'.format(e))
