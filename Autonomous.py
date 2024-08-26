#!/usr/bin/python
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

ENA = 12
IN1 = 10
IN2 = 5
IN3 = 16
IN4 = 6
ENB = 22
Trig1 = 15
Echo1 = 14
Trig2 = 24
Echo2 = 23
Trig3 = 25
Echo3 = 8
Trig4 = 17 #1
Echo4 = 27 #27 #7
Trig5 = 1
Echo5 = 7

GPIO.setup(Trig1,GPIO.OUT)
GPIO.setup(Trig2,GPIO.OUT)
GPIO.setup(Trig3,GPIO.OUT)
GPIO.setup(Trig4,GPIO.OUT)
GPIO.setup(Trig5,GPIO.OUT)
GPIO.setup(Echo1,GPIO.IN)
GPIO.setup(Echo2,GPIO.IN)
GPIO.setup(Echo3,GPIO.IN)
GPIO.setup(Echo4,GPIO.IN)
GPIO.setup(Echo5,GPIO.IN)

GPIO.setup(IN1,GPIO.OUT)
GPIO.setup(IN2,GPIO.OUT)
GPIO.setup(IN3,GPIO.OUT)
GPIO.setup(IN4,GPIO.OUT)

GPIO.setup(ENA,GPIO.OUT)
GPIO.setup(ENB,GPIO.OUT)

MTA1 = GPIO.PWM(ENA,100)
MTA2 = GPIO.PWM(ENB,100)

MTA1.start(0) # motor right
MTA2.start(0) # motor left

def CalDistance(TrigPin,EchoPin):
    GPIO.output(TrigPin,0)
    time.sleep(2E-6)
    GPIO.output(TrigPin,1)
    time.sleep(10E-6)
    GPIO.output(TrigPin,0)
    while GPIO.input(EchoPin) == 0:
        pass
    EchoStartTime = time.time()
    while GPIO.input(EchoPin) == 1:
        pass
    EchoStopTime = time.time()
    ptt = EchoStopTime - EchoStartTime
    distance = ptt * 1000000 / 2 /29.412
    return distance
def Forward():
    GPIO.output(IN1,0)
    GPIO.output(IN2,1)
    GPIO.output(IN3,0)
    GPIO.output(IN4,1)
    MTA1.ChangeDutyCycle(100)
    MTA2.ChangeDutyCycle(100)
def TurnRight():
    GPIO.output(IN1,0)
    GPIO.output(IN2,1)
    GPIO.output(IN3,0)
    GPIO.output(IN4,1)
    MTA1.ChangeDutyCycle(0)
    MTA2.ChangeDutyCycle(100)
def TurnLeft():
    GPIO.output(IN1,0)
    GPIO.output(IN2,1)
    GPIO.output(IN3,0)
    GPIO.output(IN4,1)
    MTA1.ChangeDutyCycle(100)
    MTA2.ChangeDutyCycle(0)
def StopRun():
    GPIO.output(IN1,1)
    GPIO.output(IN2,1)
    GPIO.output(IN3,1)
    GPIO.output(IN4,1)
    MTA1.ChangeDutyCycle(100)
    MTA2.ChangeDutyCycle(100)
def MeasureDis():
    global UpperRightDis
    global LowerRightDis
    global UpperLeftDis
    global LowerLeftDis
    global FrontDis
    UpperRightDis = round(CalDistance(Trig1,Echo1),2)
    LowerRightDis = round(CalDistance(Trig4,Echo4),2)
    UpperLeftDis = round(CalDistance(Trig3,Echo3),2)
    LowerLeftDis = round(CalDistance(Trig2,Echo2),2)
    FrontDis = round(CalDistance(Trig5,Echo5),2)
    
StopRun()
SetPoint = 10.00
Kp = 7
Ki = 0 
Kd = 0
	
BaseSpeed = 40
SpeedChange = 0
ErrorSum = 0 
PrevError = 0

S_Kp = 10 #8
S_Ki = 0 #.15
S_Kd = 1 #5
S_ErrorSum = 0
S_PrevError = 0
cnt = 0
def Track_Left_Wall():
    global ErrorSum
    global PrevError
    global S_ErrorSum
    global S_PrevError
    global cnt
    while True:
        time.sleep(.1)
        UpperLeftDis = round(CalDistance(Trig3,Echo3),2)
        LowerLeftDis = round(CalDistance(Trig2,Echo2),2)
        FrontDis = round(CalDistance(Trig5,Echo5),2)
        print('UpperLeftDis',UpperLeftDis)
        print('LowerLeftDis',LowerLeftDis)
        print('FrontDis',FrontDis)
        SpeedChange = 0
        if FrontDis < 25 and FrontDis > 3:
            cnt = cnt+1
            #GPIO.cleanup()
        if cnt == 3:
            ErrorSum = 0
            PrevError = 0
            S_ErrorSum = 0
            S_PrevError = 0
            cnt = 0
            TurnRight()
            time.sleep(1.2)
        if LowerLeftDis > UpperLeftDis:
            LeftDis = UpperLeftDis + (LowerLeftDis-UpperLeftDis)/2
        else:
            LeftDis = LowerLeftDis + (UpperLeftDis-LowerLeftDis)/2
        S_Error = LowerLeftDis - UpperLeftDis + 3.5
        S_Kp_total = S_Kp*S_Error
        S_ErrorSum += S_Error
        S_Ki_total = S_Ki*S_ErrorSum
        S_ErrorDiff = S_Error - S_PrevError
        S_Kd_total = S_Kd*S_ErrorDiff
        S_PrevError = S_Error
        S_Total = round(S_Kp_total+S_Ki_total+S_Kd_total,2)
        if abs(S_Error) < 2 :
            Error = round(LeftDis - SetPoint - 3,2)
            Kp_total = Kp*Error
            ErrorSum += Error
            Ki_total = Ki*ErrorSum
            ErrorDiff = round(Error - PrevError,2)
            Kd_total = Kd*ErrorDiff
            Total = round(Kp_total + Ki_total + Kd_total,2)
            PrevError = Error
            SpeedChange = Total/20
        else:
            SpeedChange = 0
        Speed2 = BaseSpeed  + S_Total - SpeedChange
        Speed1 = BaseSpeed  - S_Total + SpeedChange
        if Speed1 > 100:
            Speed1 = 100
        if Speed2 > 100:
            Speed2 = 100
        if Speed1 < -100:
            Speed1 = -100
        if Speed2 < -100:
            Speed2 = -100
        if Speed1 < 0 and Speed2 > 0:
            GPIO.output(IN1,1)
            GPIO.output(IN2,0)
            GPIO.output(IN3,0)
            GPIO.output(IN4,1)
            Speed1 = abs(Speed1)
            MTA1.ChangeDutyCycle(Speed1)
            MTA2.ChangeDutyCycle(Speed2)
        elif Speed2 < 0 and Speed1 > 0:
            GPIO.output(IN1,0)
            GPIO.output(IN2,1)
            GPIO.output(IN3,1)
            GPIO.output(IN4,0)
            Speed2 = abs(Speed2)
            MTA1.ChangeDutyCycle(Speed1)
            MTA2.ChangeDutyCycle(Speed2)
        elif Speed1 > 0 and Speed2 > 0:
            GPIO.output(IN1,0)
            GPIO.output(IN2,1)
            GPIO.output(IN3,0)
            GPIO.output(IN4,1)
            MTA1.ChangeDutyCycle(Speed1)
            MTA2.ChangeDutyCycle(Speed2)
    
def Track_Right_Wall():
    global cnt
    global ErrorSum
    global PrevError
    global S_ErrorSum
    global S_PrevError
    while True:
        time.sleep(.1)
        UpperRightDis = round(CalDistance(Trig1,Echo1),2)
        LowerRightDis = round(CalDistance(Trig4,Echo4),2)
        FrontDis = round(CalDistance(Trig5,Echo5),2)
        print('UpperRightDis',UpperRightDis)
        print('LowerRightDis',LowerRightDis)
        print('FrontDis',FrontDis)
        print('cnt',cnt)
        SpeedChange = 0
        if FrontDis < 25 and FrontDis > 3:
            cnt = cnt + 1
#             time.sleep(1.2)
            #GPIO.cleanup()
        if cnt == 3:
            ErrorSum = 0
            PrevError = 0
            S_ErrorSum = 0
            S_PrevError = 0
            TurnLeft()
            time.sleep(1.2)
            cnt = 0
        if UpperRightDis > LowerRightDis:
            RightDis = LowerRightDis + (UpperRightDis-LowerRightDis)/2
        else:
            RightDis = UpperRightDis + (LowerRightDis-UpperRightDis)/2
        S_Error = UpperRightDis - LowerRightDis + 0.5
        S_Kp_total = 10*S_Error
        S_ErrorSum += S_Error
        S_Ki_total = S_Ki*S_ErrorSum
        S_ErrorDiff = S_Error - S_PrevError
        S_Kd_total = 2*S_ErrorDiff
        S_PrevError = S_Error
        S_Total = round(S_Kp_total+S_Ki_total+S_Kd_total,2)
        if abs(S_Error) < 1 :
            Error = round(RightDis - SetPoint -3,2)
            Kp_total = Kp*Error
            ErrorSum += Error
            Ki_total = Ki*ErrorSum
            ErrorDiff = round(Error - PrevError,2)
            Kd_total = Kd*ErrorDiff
            Total = round(Kp_total + Ki_total + Kd_total,2)
            PrevError = Error
            SpeedChange = Total/20
        else:
            SpeedChange = 0

        Speed2 = BaseSpeed  + S_Total + SpeedChange
        Speed1 = BaseSpeed  - S_Total - SpeedChange
        if Speed1 > 100:
            Speed1 = 100
        if Speed2 > 100:
            Speed2 = 100
        if Speed1 < -100:
            Speed1 = -100
        if Speed2 < -100:
            Speed2 = -100
        if Speed1 < 0 and Speed2 > 0:
            GPIO.output(IN1,1)
            GPIO.output(IN2,0)
            GPIO.output(IN3,0)
            GPIO.output(IN4,1)
            Speed1 = abs(Speed1)
            MTA1.ChangeDutyCycle(Speed1)
            MTA2.ChangeDutyCycle(Speed2)
        elif Speed2 < 0 and Speed1 > 0:
            GPIO.output(IN1,0)
            GPIO.output(IN2,1)
            GPIO.output(IN3,1)
            GPIO.output(IN4,0)
            Speed2 = abs(Speed2)
            MTA1.ChangeDutyCycle(Speed1)
            MTA2.ChangeDutyCycle(Speed2)
        elif Speed1 > 0 and Speed2 > 0:
            GPIO.output(IN1,0)
            GPIO.output(IN2,1)
            GPIO.output(IN3,0)
            GPIO.output(IN4,1)
            MTA1.ChangeDutyCycle(Speed1)
            MTA2.ChangeDutyCycle(Speed2)
            
def FindWall():
    UpperRightDis = round(CalDistance(Trig1,Echo1),2)
    LowerRightDis = round(CalDistance(Trig4,Echo4),2)
    UpperLeftDis = round(CalDistance(Trig3,Echo3),2)
    LowerLeftDis = round(CalDistance(Trig2,Echo2),2)
    time.sleep(.5)
    if UpperLeftDis < UpperRightDis and LowerLeftDis < LowerRightDis:
        Track_Left_Wall()
    elif UpperLeftDis > UpperRightDis and LowerLeftDis > LowerRightDis:
        Track_Right_Wall()

# StopRun()
while True:
#     time.sleep(.5)

#     GPIO.output(IN1,0)
#     GPIO.output(IN2,1)

#     GPIO.output(6,1)
#     GPIO.output(IN4,1)
#     MTA1.ChangeDutyCycle(100)
#     MTA2.ChangeDutyCycle(50)

    #print('UpperLeftDis',UpperLeftDis)
    #print('LowerLeftDis',LowerLeftDis)
    #print('FrontDis',FrontDis)
    #GPIO.cleanup()
#     Forward()
    FindWall()
    
