# Robot Control system
# fernando.lourenco@lourenco.eu

VERSION = "0.1.2"

import RPi.GPIO as GPIO
from time import sleep, time
import argparse
import serial
import hardware
import datetime

import traceback

import xlrd
import csv

from ConfigParser import SafeConfigParser
import codecs

import math

global port
global logfile
global writelog

global speed1, speed2

global highspeed
highspeed = False

global xpos, ypos, alphapos

def readserial():
    start = time()
    buffer = ''
    ch = ''
    while (time()-start<0.5) and (ch != '\n'):
        ch = port.read()
        if ch !='':
            buffer += chr(ord(ch))
            #print "ch=", ch, ' - ' , ord(ch), ' - ' , (ch=='\n')

    #print "buffer = ", buffer, " -> ", len(buffer), " caracteres"
    return buffer

def mededistancia():
    distancia = 0
    ntent = 3

    while (distancia == 0) and (ntent>0):
        port.flushInput()
        port.flushOutput()

        port.write("D\n")
        resposta = readserial()

        try:
            distancia = float(resposta)
        except:
            distancia = 0

        resposta = readserial()

        ntent -= 1

    return distancia

def roda(angulo):
    port.flushInput()
    port.flushOutput()

    port.write("A%d\n" % angulo)
    sleep(2)
    resposta = readserial()

def ligamotoresfrente(distancia, highspeed):
    print "Distance %7.2f cm; Highspeed = %s; Hour = %s" % (distancia, repr(highspeed), datetime.datetime.now().time())
    writelog.writerow([distancia, repr(highspeed), datetime.datetime.now().time()])

    GPIO.output(hardware.motorFEIA, 0)
    GPIO.output(hardware.motorFEIB, 1)

    GPIO.output(hardware.motorTDIA, 1)
    GPIO.output(hardware.motorTDIB, 0)

    if highspeed == True:
        GPIO.output(hardware.motorFDIA, 1)
        GPIO.output(hardware.motorFDIB, 0)

        GPIO.output(hardware.motorTEIA, 0)
        GPIO.output(hardware.motorTEIB, 1)
    else:
        GPIO.output(hardware.motorFDIA, 0)
        GPIO.output(hardware.motorFDIB, 0)

        GPIO.output(hardware.motorTEIA, 0)
        GPIO.output(hardware.motorTEIB, 0)

def ligamotorestras(distancia, highspeed):
    print "Distance %7.2f cm; Highspeed = %s; Hour = %s" % (distancia, repr(highspeed), datetime.datetime.now().time())
    writelog.writerow([distancia, repr(highspeed), datetime.datetime.now().time()])

    GPIO.output(hardware.motorFDIA, 0)
    GPIO.output(hardware.motorFDIB, 1)

    GPIO.output(hardware.motorTEIA, 1)
    GPIO.output(hardware.motorTEIB, 0)

    if highspeed == True:
        GPIO.output(hardware.motorFEIA, 1)
        GPIO.output(hardware.motorFEIB, 0)

        GPIO.output(hardware.motorTDIA, 0)
        GPIO.output(hardware.motorTDIB, 1)
    else:
        GPIO.output(hardware.motorFEIA, 0)
        GPIO.output(hardware.motorFEIB, 0)

        GPIO.output(hardware.motorTDIA, 0)
        GPIO.output(hardware.motorTDIB, 0)

def andafrenteatebater():
    distancia = 999
    highspeed = False

    while (distancia>10):
        ligamotoresfrente(distancia, highspeed)

        distancia = mededistancia()

        if distancia > 40:
            highspeed = True
        else:
            highspeed = False

            if distancia<25:
                para()
                if distancia>10:
                    ligamotoresfrente(distancia, highspeed)
                    sleep(distancia/speed1)
                    para()

                    distancia = mededistancia()
                    print "Distance %7.2f cm; Highspeed = %s; Hour = %s" % (distancia, repr(highspeed), datetime.datetime.now().time())

    para()

def readcompass():
    compass = 0
    ntent = 3

    while (compass == 0) and (ntent>0):
        port.flushInput()
        port.flushOutput()

        port.write("C\n")
        resposta = readserial()

        try:
            compass = float(resposta)
        except:
            compass = 0

        resposta = readserial()

        ntent -= 1

    return compass

def rotatecar(angle):
    if angle<alphapos:
        #rotate right
        while alphapos>angle:
            andafrentedireita(0.1)
            alphapos = readcompass()
    else:
        #rotate left
        while alphapos<angle:
            andafrenteesquerda(0.1)
            alphapos = readcompass()

def track (xfinal, yfinal):
    print "Destination x=%d; y=%d" % (xfinal, yfinal)

    rota = atan2(yfinal-ypos, xfinal-xpos)/math.pi*180
    roda(rota)

    distancia = mededistancia()

    if distancia>math.sqrt(math.pow(yfinal-ypos,2)+math.pow(xfinal-xpos,2))+5:
        rotatecar(rota)
        #move ahead
    else:
        print "Obstacle detected! Aborting."

def andafrente(tempo):
    ligamotoresfrente(0, highspeed)
    sleep(tempo)
    para()

def andatras(tempo):
    ligamotorestras(0, highspeed)

    sleep(tempo)
    para()

def andafrentedireita(tempo):
    GPIO.output(hardware.motorFDIA, 0)
    GPIO.output(hardware.motorFDIB, 0)
    GPIO.output(hardware.motorTDIA, 0)
    GPIO.output(hardware.motorTDIB, 0)

    GPIO.output(hardware.motorFEIA, 0)
    GPIO.output(hardware.motorFEIB, 1)
    GPIO.output(hardware.motorTEIA, 0)
    GPIO.output(hardware.motorTEIB, 1)
    sleep(tempo)
    para()

def andafrenteesquerda(tempo):
    GPIO.output(hardware.motorFEIA, 0)
    GPIO.output(hardware.motorFEIB, 0)
    GPIO.output(hardware.motorTEIA, 0)
    GPIO.output(hardware.motorTEIB, 0)

    GPIO.output(hardware.motorFDIA, 1)
    GPIO.output(hardware.motorFDIB, 0)
    GPIO.output(hardware.motorTDIA, 1)
    GPIO.output(hardware.motorTDIB, 0)

    sleep(tempo)
    para()

def andatrasdireita(tempo):
    GPIO.output(hardware.motorFDIA, 0)
    GPIO.output(hardware.motorFDIB, 0)
    GPIO.output(hardware.motorTDIA, 0)
    GPIO.output(hardware.motorTDIB, 0)

    GPIO.output(hardware.motorFEIA, 1)
    GPIO.output(hardware.motorFEIB, 0)
    GPIO.output(hardware.motorTEIA, 1)
    GPIO.output(hardware.motorTEIB, 0)

    sleep(tempo)
    para()

def andatrasesquerda(tempo):
    GPIO.output(hardware.motorFEIA, 0)
    GPIO.output(hardware.motorFEIB, 0)
    GPIO.output(hardware.motorTEIA, 0)
    GPIO.output(hardware.motorTEIB, 0)

    GPIO.output(hardware.motorFDIA, 0)
    GPIO.output(hardware.motorFDIB, 1)
    GPIO.output(hardware.motorTDIA, 0)
    GPIO.output(hardware.motorTDIB, 1)

    sleep(tempo)
    para()

def para():
    GPIO.output(hardware.motorFDIA, 0)
    GPIO.output(hardware.motorFDIB, 0)
    GPIO.output(hardware.motorFEIA, 0)
    GPIO.output(hardware.motorFEIB, 0)
    GPIO.output(hardware.motorTDIA, 0)
    GPIO.output(hardware.motorTDIB, 0)
    GPIO.output(hardware.motorTEIA, 0)
    GPIO.output(hardware.motorTEIB, 0)

parser = argparse.ArgumentParser(description='Move Robot Pi Vs. %s' % VERSION, prog='Move Robot Pi %s' % VERSION)
parser.add_argument('-f', '--front', help='Move front', action='store_true', required=False)
parser.add_argument('-b', '--back', help='Move back', action='store_true',required=False)
parser.add_argument('-l', '--left', help='Move left', action='store_true', required=False)
parser.add_argument('-r', '--right', help='Move right', action='store_true', required=False)
parser.add_argument('-t', '--time', help='Time (s) optinal. Default = 1s', nargs = 1, type=float, default = [1.0], required=False)
parser.add_argument('-a', '--angle', help='Rotate servo. Default = 110 deg', nargs = 1, type=float, required=False)
parser.add_argument('-g', '--debug', help='Debug function', action='store_true', required=False)
parser.add_argument('-s', '--sensor', help='Measure distance to obstacle (in cm)', action='store_true', required=False)
parser.add_argument('-w', '--lowspeed', help='Turn on only 2 motors', action='store_true', default = False, required=False)
parser.add_argument('-p', '--stop', help='Stop all movement', action='store_true', required=False)
parser.add_argument('-c', '--track', help='xlsx file describing track to follow', nargs = 1, default = ['path-test 1.xlsx'],required=False)

parser.add_argument('-v', '--version', action='version', version='fernando.lourenco@lourenco.eu - %(prog)s')

args = parser.parse_args()

# Read time to run motors
try:
    tempo = float(args.time[0])
except:
    tempo = 1

#Define initial position and course
xpos = 0
ypos = 0
alphapos = 0

# Read config file
parser = SafeConfigParser()
# Open the file with the correct encoding
with codecs.open('4wheel.ini', 'r', encoding='utf-8') as f:
    parser.readfp(f)
speed1 = parser.get('Movement', 'speed1')
speed2 = parser.get('Movement', 'speed2')

port = serial.Serial(parser.get('Serial', 'port'), baudrate=parser.get('Serial', 'baudrate'), timeout=0.05)

#Create Logfile
logfile = open(parser.get('Log', 'logfile'), 'wb')
writelog = csv.writer(logfile, quoting=csv.QUOTE_ALL)
writelog.writerow(['Distance (cm)', 'Highspeed', 'Hour'])

# Debug purposes only
if args.debug:
    andafrenteatebater()

# Choose speed of movement
if args.lowspeed:
    highspeed = False
else:
    highspeed = True

# Stop car
if args.stop:
    para()

# Rotate servo of distance sensor
if args.angle:
    angulo = float(args.angle[0])
    roda(angulo)

# Read distance sensor
if args.sensor:
    print "Distance to obstacle is %7.2f cm" % mededistancia()

# Read track file if it exists
if args.track:
    try:
        wb = xlrd.open_workbook(args.track[0])
        sh = wb.sheet_by_name('Sheet1')

        for rownum in xrange(sh.nrows):
            linha = []
            coluna = 0
            x = 0
            y = 0
            for entry in sh.row_values(rownum):
                #print "Row=%d; Column=%d; Contents=%s" % (rownum, coluna,entry)
                if rownum<>0:
                    if coluna == 0: x = entry
                    if coluna == 1: y = entry
                coluna = coluna+1
            if rownum<>0: track(x,y)

    except Exception:
        print "Can't open file '%s'" % args.track[0]
        #traceback.print_exc()

if args.front:
    if args.right:
        andafrentedireita(tempo)
    elif args.left:
        andafrenteesquerda(tempo)
    else:
        andafrente(tempo)
elif args.back:
    if args.right:
        andatrasdireita(tempo)
    elif args.left:
        andatrasesquerda(tempo)
    else:
        andatras(tempo)

#Clean-up
para()
GPIO.cleanup()

logfile.close()