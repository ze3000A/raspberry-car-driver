#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 07:51:54 
Shenzhen Yahboom Tech

@author: LONGFU SUN
"""

from __future__ import division
import time
import Adafruit_PCA9685
import serial
import string
import RPi.GPIO as GPIO

CarSpeedControl = 2000
g_CarState = 0 
NewLineReceived = 0
InputStringcache = ''
pwm = Adafruit_PCA9685.PCA9685()


LED8=8
LED9=9
LED10=10
LED11=11

LINA=12
LINB=13
RLNA=14
RLNB=15

LED0=0
LED1=1
LED2=2
LED3=3

SERVO=7
InputString = ''



#状态值定义
enSTOP = 0
enRUN =1
enBACK = 2
enLEFT = 3
enRIGHT = 4
enTLEFT =5
enTRIGHT = 6

run_car  = '1'  #按键前
back_car = '2'  #按键后
left_car = '3'  #按键左
right_car = '4' #按键右
stop_car = '0'  #按键停

pwm.set_pwm_freq(50)

#最大频率是4096，4096时达到最高速度，1024，2048，3072
#向前，两个舵机向相同方向旋转


def back(Speed):
    pwm.set_pwm(LED8,0,Speed)
    pwm.set_pwm(LED9,0,0)
    pwm.set_pwm(LED11,0,Speed)
    pwm.set_pwm(LED10,0,0)
    pwm.set_pwm(LED0,0,Speed)
    pwm.set_pwm(LED1,0,0)
    pwm.set_pwm(LED3,0,Speed)
    pwm.set_pwm(LED2,0,0)
    pwm.set_pwm(LINA,0,Speed)
    pwm.set_pwm(LINB,0,0)
    pwm.set_pwm(RLNB,0,Speed)
    pwm.set_pwm(RLNA,0,0)


def run(Speed):
    pwm.set_pwm(LED8,0,0)
    pwm.set_pwm(LED9,0,Speed)
    pwm.set_pwm(LED11,0,0)
    pwm.set_pwm(LED10,0,Speed)
    pwm.set_pwm(LED0,0,0)
    pwm.set_pwm(LED1,0,Speed)
    pwm.set_pwm(LED3,0,0)
    pwm.set_pwm(LED2,0,Speed)
    pwm.set_pwm(LINA,0,0)
    pwm.set_pwm(LINB,0,Speed)
    pwm.set_pwm(RLNB,0,0)
    pwm.set_pwm(RLNA,0,Speed)


def brake():
    pwm.set_pwm(LED8,0,0)
    pwm.set_pwm(LED9,0,0)
    pwm.set_pwm(LED11,0,0)
    pwm.set_pwm(LED10,0,0)
    pwm.set_pwm(LED0,0,0)
    pwm.set_pwm(LED1,0,0)
    pwm.set_pwm(LED3,0,0)
    pwm.set_pwm(LED2,0,0)
    pwm.set_pwm(LINA,0,0)
    pwm.set_pwm(LINB,0,0)
    pwm.set_pwm(RLNB,0,0)
    pwm.set_pwm(RLNA,0,0)


def left(Speed):
    pwm.set_pwm(LED8,0,Speed)
    pwm.set_pwm(LED9,0,0)
    pwm.set_pwm(LED11,0,0)
    pwm.set_pwm(LED10,0,Speed)
    pwm.set_pwm(LED0,0,Speed)
    pwm.set_pwm(LED1,0,0)
    pwm.set_pwm(LED3,0,0)
    pwm.set_pwm(LED2,0,Speed)
    pwm.set_pwm(LINA,0,Speed)
    pwm.set_pwm(LINB,0,0)
    pwm.set_pwm(RLNB,0,0)
    pwm.set_pwm(RLNA,0,Speed)


def right(Speed):
    pwm.set_pwm(LED8,0,0)
    pwm.set_pwm(LED9,0,Speed)
    pwm.set_pwm(LED11,0,Speed)
    pwm.set_pwm(LED10,0,0)
    pwm.set_pwm(LED0,0,0)
    pwm.set_pwm(LED1,0,Speed)
    pwm.set_pwm(LED3,0,Speed)
    pwm.set_pwm(LED2,0,0)
    pwm.set_pwm(LINA,0,0)
    pwm.set_pwm(LINB,0,Speed)
    pwm.set_pwm(RLNB,0,Speed)
    pwm.set_pwm(RLNA,0,0)

    
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)
    
def set_servo_angle(channel,angle):
    angle=4096*((angle*11)+500)/20000
    pwm.set_pwm(channel,0,int(angle))
    
#串口数据解析并指定相应的动作
def serial_data_parse():
    global NewLineReceived
    global g_CarState
    global red
    global green
    global blue
    global CarSpeedControl
    #解析上位机发来的舵机云台的控制指令并执行舵机旋转
    #如:$4WD,PTZ180# 舵机转动到180度	
    if (InputString.find("$4WD,PTZ", 0, len(InputString)) != -1):
        i = InputString.find("PTZ",  0, len(InputString)) 
        ii = InputString.find("#",  0, len(InputString))
        if ii > i:
        	string = InputString[i+3:ii]
		m_kp = int(string)
		set_servo_angle(7,180 - m_kp)
		NewLineReceived = 0
		InputString.zfill(len(InputString))
		print "in"
		print InputString

    if (InputString.find("$4WD", 0, len(InputString)) == -1) and (InputString.find("#",  0, len(InputString)) != -1):
        if InputString[3] == '1':
            g_CarState = enTLEFT
            print "g_CarState: %d" % g_CarState
        elif InputString[3] == '2':
            g_CarState = enTRIGHT
        else:
            g_CarState = enSTOP

        if InputString[9] == '1':
            set_servo_angle(7,180)
        if InputString[9] == '2':
            set_servo_angle(7,0)
        if InputString[17] == '1':
            set_servo_angle(7,90)
        
        if InputString[7] == '1':
            CarSpeedControl += 1000
            if CarSpeedControl >4095:
                CarSpeedControl=4095
        if InputString[7] == '2':
            CarSpeedControl -= 1000
            if CarSpeedControl <0:
                CarSpeedControl=500

        if g_CarState != enTLEFT and g_CarState != enTRIGHT:
            print "hellonice"
            print run_car
            print InputString[1]
            if InputString[1] == run_car:
                g_CarState = enRUN
                print "run car"
            elif InputString[1] == back_car:
                g_CarState = enBACK	
            elif InputString[1] == left_car:
                g_CarState = enLEFT
            elif InputString[1] == right_car:
                g_CarState = enRIGHT
            elif InputString[1] == stop_car:
                g_CarState = enSTOP
            else:
                g_CarState = enSTOP				  
        NewLineReceived = 0
        InputString.zfill(len(InputString))	

def serialEvent():
    global InputString
    global InputStringcache
    global StartBit
    global NewLineReceived
    InputString = ''
    while NewLineReceived == 0 :
        size = ser.inWaiting()
        if size == 0:
           
            break
        else:
            while size != 0:
                serialdatabit = ser.read(1)
                size -= 1
                if serialdatabit == '$':
                    StartBit = 1
                if StartBit == 1:
                    InputStringcache += serialdatabit
                if StartBit == 1 and serialdatabit == '#':
                    NewLineReceived = 1
                    InputString = InputStringcache
                    InputStringcache = ''
                    StartBit = 0
                    size = 0
                    print InputString





GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

GPIO.output(17,False)
time.sleep(2)
GPIO.output(17,True)

try:
 


    ser = serial.Serial("/dev/ttyAMA0", 9600, timeout = 0.001)
    print "serial.isOpen() = ",ser.isOpen()
    ser.write("serial is on!")
    while True:
        serialEvent()
       #time.sleep(0.4)
    	if NewLineReceived == 1:
    		print "serialdata:%s" % InputString
    		serial_data_parse()
    		NewLineReceived = 0

            #print "nice to meet you"	
    	if g_CarState == enSTOP:
    	    brake()                   
    	elif g_CarState == enRUN:
    	    run(CarSpeedControl)
    	elif g_CarState == enLEFT:
    	    left(CarSpeedControl)
    	elif g_CarState == enRIGHT:
    	    right(CarSpeedControl)
    	elif g_CarState == enBACK:
    	    back(CarSpeedControl)
    	elif g_CarState == enTLEFT:
    	    left(CarSpeedControl)
    	elif g_CarState == enTRIGHT:
    	    right(CarSpeedControl)
    	else:
    	    brake()
        
except KeyboardInterrupt:
    pass

ser.close()
GPIO.cleanup()

