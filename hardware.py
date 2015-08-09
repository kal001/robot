import RPi.GPIO as GPIO

global motorFEIA
global motorFEIB
global motorFDIA
global motorFDIB
global motorTEIA
global motorTEIB
global motorTDIA
global motorTDIB
global sensorpin

motorFEIA = 18
motorFEIB = 7
motorFDIA = 23
motorFDIB = 24
motorTEIA = 25
motorTEIB = 8
motorTDIA = 16
motorTDIB = 20
sensorpin = 12

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(motorFEIA, GPIO.OUT)
GPIO.setup(motorFEIB, GPIO.OUT)
GPIO.setup(motorFDIA, GPIO.OUT)
GPIO.setup(motorFDIB, GPIO.OUT)
GPIO.setup(motorTEIA, GPIO.OUT)
GPIO.setup(motorTEIB, GPIO.OUT)
GPIO.setup(motorTDIA, GPIO.OUT)
GPIO.setup(motorTDIB, GPIO.OUT)
GPIO.setup(sensorpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)