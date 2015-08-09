VERSION = "0.1.0"

import RPi.GPIO as GPIO
from time import sleep, time
import argparse
import serial
import hardware
import datetime

global port

global speed1
speed1 = 40.0 # low speed. only 2 front motors running. cm/s
global speed2
speed2 = 40.0 # high speed. 2 front motors and 2 rear motors running. cm/s
global highspeed
highspeed = False

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

parser.add_argument('-v', '--version', action='version', version='fernando.lourenco@lourenco.eu - %(prog)s')

args = parser.parse_args()

port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=0.05)

try:
    tempo = float(args.time[0])
except:
    tempo = 1

if args.debug:
    andafrenteatebater()

if args.lowspeed:
    highspeed = False
else:
    highspeed = True

if args.stop:
    para()

if args.angle:
    angulo = float(args.angle[0])
    roda(angulo)

if args.sensor:
    print "Distance to obstacle is %7.2f cm" % mededistancia()

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

para()
GPIO.cleanup()
