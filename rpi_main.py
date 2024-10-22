
import firebase_admin
from firebase_admin import credentials, db, firestore
import RPi.GPIO as GPIO
import time


cred = credentials.Certificate('./anti-theft-detection-2d6d8-firebase-adminsdk.json')
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()
doc_ref = db.collection('cameralog')
doc_ref2 = db.collection('entrylog')

TRIG1 = 23
ECHO1 = 24
servo_pin = 18
buzzer_pin = 17

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)
GPIO.setup(servo_pin,GPIO.OUT)
# p = GPIO.PWM(servo_pin, 50)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)
GPIO.setup(buzzer_pin, GPIO.OUT)


# to update the camera-on variable depending on whether a person is detected
#if detected
docs = (
    doc_ref
    .where("cameraOn", "==", "false")
    .stream()
)

def setTrue():
    docs = (
        doc_ref
        .where("cameraOn", "==", "false")
        .stream()
    )
    for doc in docs:
        doc_ref.document(doc.id).set({"cameraOn":"true"}, merge = True)

def setFalse():
    docs = (
        doc_ref
        .where("cameraOn", "==", "true")
        .stream()
    )
    for doc in docs:
        doc_ref.document(doc.id).set({"cameraOn":"false"}, merge = True)


def getDistance():
    GPIO.output(TRIG1, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(TRIG1, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG1, GPIO.LOW)
    while GPIO.input(ECHO1) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO1) == 1:
        pulse_end = time.time()
    pulse_duration1 = pulse_end - pulse_start
    distance1 = pulse_duration1 * 17150
    distance1 = round(distance1, 2)
    print("Distance: ",distance1)
    if (distance1 > 0):
        setTrue()
        time.sleep(5)
        setFalse()

def set_angle(angle):
    duty = 2 + (angle / 18)  # Convert angle to duty cycle
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)


def door():
    # docs = (
    #     doc_ref2
    #     .where("name", "==", "unknown")
    #     .stream()
    # )
    # for doc in docs:
    #     while True:
    #         if doc.to_dict()['canAccess'] == False:
    #             print("r")
    #             while True:
    #                 if doc.to_dict()['canAccess'] == True:
    #                     print("Door Open")
    #                     break
    #             time.sleep(2)
    #             break
    #         time.sleep(2)

    # p.start(0)               # Starts running PWM on the pin and sets it to 0
    # # Move the servo back and forth
    # p.ChangeDutyCycle(3)     # Changes the pulse width to 3 (so moves the servo)
    # time.sleep(1)                 # Wait 1 second
    # p.ChangeDutyCycle(12)    # Changes the pulse width to 12 (so moves the servo)
    # time.sleep(1)
    # # Clean up everything
    # p.stop()
    try:
        while True:
            print("door")
            # Rotate servo to 0 degrees
            set_angle(0)
            time.sleep(2)
            
            # Rotate servo to 90 degrees
            set_angle(90)
            time.sleep(2)
            
            # Rotate servo to 180 degrees
            set_angle(180)
            time.sleep(2)

    except KeyboardInterrupt:
        pass

    # Stop the PWM and cleanup
    pwm.stop()

def alarm():
    try:
        while True:
            docs = (
                    doc_ref
                    .where("alarmOn", "==", "true")
                    .stream()
                )
            for doc in docs:
                # print(doc)
                GPIO.output(buzzer_pin, GPIO.HIGH)
                print("Buzzer ON")
                time.sleep(1)  # Beep for 1 second
                
                # Turn the buzzer OFF
                GPIO.output(buzzer_pin, GPIO.LOW)
                print("Buzzer OFF")
                time.sleep(1)  # Silence for 1 second

    except KeyboardInterrupt:
        print("GPIO cleanup complete")

# getDistance()
door()
# alarm()