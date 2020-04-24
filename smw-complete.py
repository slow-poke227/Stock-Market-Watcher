from alpha_vantage.timeseries import TimeSeries
from datetime import datetime
from datetime import timedelta
from datetime import date
import datetime
import time
import RPi.GPIO as GPIO

# initializing global variables
key = '__your_key_here__'  # your API key
symbol = ''  # equity name
data = "4. close"  # string to filter through API response
ts = TimeSeries(key)  # initial API call (see getEquityValues())
goal = 1.25  # initialize goal, also acts as note if goal did not save correctly
# initialize light values as all off
lights = {'l1': [False, False, False],
          'l2': [False, False, False],
          'l3': [False, False, False]}
# initialize board
GPIO.setmode(GPIO.BOARD)
# counter for light loop
counter = 0


# main loop
def main():
    loop = True
    x = 0
    while loop:
        print("Please select from the options below:")
        printVars()
        x = int(input())

        if x == 1:
            # Set the goal number(real) for third light in sequence
            setGoalAmount()
            print("------------------------------------------------")
        elif x == 2:
            # change stock name
            changeEquityName()
            print("------------------------------------------------")
        elif x == 3:
            print("Updating equity values")
            print("This selection is currently Out of Order due to API restrictions")
            print("Please make another selection in teh meantime")
            print("------------------------------------------------")
            # updating the values will cause the API to halt due to usage restrictions
            # currently this option will do nothing
            #updateEquityValues()
        elif x == 4:
            print("Starting program as usual")
            getEquityValues()
            boardSetup()
            testlights()
            boardClean()
            print("------------------------------------------------")
        elif x == 5:
            print("Now exiting...")
            loop = False
        else:
            print("------------------------------------------------")
            print("That is not a valid response, please input a number 1-5")
            print("------------------------------------------------")

# fctn for saving values to file
def writeToFile(symbol, goal):
    spam = open("smw-sg.txt", "w")
    spam.write(symbol + "\n" + str(goal))
    spam.close()

# fctn for retrieving vars from file
def getStoredVars():
    global symbol
    global goal
    symbol = getSymbol()
    goal = getGoal()
    # print vars on startup
    print(symbol + " is current symbol")
    print(goal + " is current goal")
    print("----------------------")

def getGoal():
    spam = open("smw-sg.txt", "r")
    cnt = 0
    for line in spam:
        cnt = cnt + 1
        if cnt == 3:
            return line
    spam.close()

def getSymbol():
    spam = open("smw-sg.txt", "r")
    cnt = 0
    for line in spam:
        cnt = cnt + 1
        if cnt == 1:
            return line
    spam.close()

# NOTE: this pinout is for the RPi 3b+
def boardSetup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.OUT)
    GPIO.output(7, GPIO.HIGH)
    GPIO.setup(11, GPIO.OUT)
    GPIO.output(11, GPIO.HIGH)
    GPIO.setup(13, GPIO.OUT)
    GPIO.output(13, GPIO.HIGH)


def testlights():
    global counter
    for key in lights:
        print("Current key is: ")
        print(key)
        print('---------------------')
        print("coutner is :")
        print(counter)
        counter = counter + 1
        if lights[key][0] == True:
            GPIO.output(7, GPIO.LOW)
            print("GREEN")
        elif lights[key][2] == True:
            GPIO.output(13, GPIO.LOW)
            print("RED")
        elif lights[key][1] == True:
            GPIO.output(11, GPIO.LOW)
            print("YELLOW")
        print('End round ', counter)
        time.sleep(5)
        GPIO.cleanup()
        boardSetup()

# reset board pins
def boardClean():
    GPIO.cleanup()


def l1Check(lastMostCurrent, prevMostCurrent):
    global lights
    if lastMostCurrent > prevMostCurrent:
        lights['l1'][0] = True
    elif lastMostCurrent <= prevMostCurrent:
        lights['l1'][2] = True
    else:
        lights['l1'][1] = True


def l2Check(lastMostCurrent, lastClose):
    global lights
    if lastMostCurrent > lastClose:
        lights['l2'][0] = True
    elif lastMostCurrent <= lastClose:
        lights['l2'][2] = True
    else:
        lights['l2'][1] = True


def l3Check(lastMostCurrent):
    global lights
    global goal
    if float(lastMostCurrent) > float(goal):
        lights['l3'][0] = True
    elif float(lastMostCurrent) <= float(goal):
        lights['l3'][2] = True
    else:
        lights['l3'][1] = True

# in order: lastMostCurrent, prevMostCurrent, lastClose
def lightSequence(foo, bar, spam):
    l1Check(foo, bar)
    l2Check(foo, spam)
    l3Check(foo)


def setGoalAmount():
    print("This option is to set the target sell price you would like to watch")
    global goal
    global symbol
    foo = True
    bar = True
    z = ''
    while foo:
        print("Your current goal value is: ", goal)
        print("If this value is correct, press 'y', and if not, press 'n'")
        z = input()
        if z == 'y':
            foo = False
        elif z == 'n':
            print("enter the desired goal")
            while bar:
                try:
                    goal = float(input())
                except ValueError:
                    print("Oops! That isn't a number!")
                else:
                    break
        else:
            print("that is not a valid argument, please enter a valid option (y/n)")
    # small fctn to write new var into storage file
    writeToFile(symbol, goal)


# update equity values
def updateEquityValues():
    global symbol
    realSymbol = symbol.rstrip("\n")
    # currently the month api is unnecessary
    # api call for last month
    # amdLM, metaLM = ts.get_monthly(symbol)
    # api call for lastDay
    amdYD, metaYD = ts.get_daily(realSymbol)
    # api call to grab most recent data set
    amdMR, metaMR = ts.get_intraday(realSymbol)


# change equity symbol
def changeEquityName():
    print("This option is to change the equity symbol")
    print("------------------------------------------------")
    global goal
    global symbol
    y = ''
    while y != 'y':
        print("Your current equity symbol is ", symbol)
        print("If this is the desired symbol, type 'y', if not type 'n'")
        y = input()
        if y == 'n':
            print("Please enter the desired equity symbol")
            symbol = input().upper()
            symbol = symbol + "\n"
        elif y != 'y':
            print("That is not a valid input, please try again")
    # write values
    writeToFile(symbol, goal)


# main loop options print statement
def printVars():
    print("1. Set or change equity goal amount")
    print("2. Change equity symbol")
    print("3. Update equity values")
    print("4. Start sequence")
    print("5. Exit program")


def getEquityValues():
    global symbol
    realSymbol = symbol.rstrip("\n")
    # api call for lastDay
    amdYD, metaYD = ts.get_daily(realSymbol)
    # api call to grab most recent data set
    amdMR, metaMR = ts.get_intraday(realSymbol)

    # today's date in 'YYYY-MM-DD'
    today = datetime.date.today()
    # make sure today is a weekday
    # if not find last weekday and warn user
    while today.isoweekday() > 5:
        print("The stock market was not open this day..")
        print("Using last valid date for data")
        today = today - timedelta(days=1)

    # YESTERDAY CLOSE
    # yesterday's date in 'YYYY-MM-DD'
    yesterday = today - timedelta(days=1)
    while yesterday.isoweekday() > 5:
        print("The stock market was not open this day")
        print("using last valid date")
        yesterday = yesterday - timedelta(days=1)

    # get data for yesterday
    fieldYD = amdYD[str(yesterday)]
    # limit to wanted data (close)
    lastClose = fieldYD[data]

    # MOST RECENT CALL
    # make dict using returned data
    mostRecentTimes = amdMR.keys()
    # set equal to first key name
    mostRecentCall = list(mostRecentTimes)[0]
    # get value using the key
    lastMR = amdMR[mostRecentCall]
    # limit to wanted data (close)
    lastMostCurrent = lastMR[data]

    # LAST MOST CURRENT
    # use same dict mostRecentTimes
    # set equal to second key name
    lastMostRecentCall = list(mostRecentTimes)[1]
    # get value using key
    prevMR = amdMR[lastMostRecentCall]
    # limit to wanted data (close)
    prevMostCurrent = prevMR[data]

    lightSequence(lastMostCurrent, prevMostCurrent, lastClose)

    # print("last month's close was: ")
    # print(lastMonth)
    print("The close at the end of yesterday was: ")
    print(lastClose)
    print("Last time stamp the close was: ")
    print(prevMostCurrent)
    print("The most recent time stamp shows a close of: ")
    print(lastMostCurrent)


# Call main loop
if __name__ == "__main__":
    getStoredVars()
    main()

