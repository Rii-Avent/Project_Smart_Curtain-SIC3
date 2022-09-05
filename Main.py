from pickletools import long1
import time
import requests
import math
import random
from tkinter import Variable
import Adafruit_DHT

import RPi.GPIO as GPIO



TOKEN = "....."  
DEVICE_LABEL = "...."   
VARIABLE_LABEL_1 = "LDR"  
VARIABLE_LABEL_2 = "SUHU"
VARIABLE_LABEL_3 = "KELEMBABAN"
VARIABLE_LABEL_4 = "POSISI"


GPIO.setmode(GPIO.BOARD)


GPIO.setup(12,GPIO.OUT)
servo1 = GPIO.PWM(12,50) 
servo1.start(0)
print ("Servo1 dijalankan")
time.sleep(2)

GPIO.setup(18,GPIO.OUT)
servo2 = GPIO.PWM(18,50)
servo2.start(0)
print ("Servo2 dijalankan")
time.sleep(2)

GPIO.setmode(GPIO.BOARD)



kelembaban = 0
suhu = 0

def build_payload(pin_to_circuit, varia_2, varia_3, varia_4):
    global kelembaban, suhu
    GPIO.setmode(GPIO.BOARD)
    pin_to_circuit = 11

    hitung = 0

    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(5)
    GPIO.setup(pin_to_circuit, GPIO.IN)
  
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):

        hitung += 1
    
    DHT_SENSOR = Adafruit_DHT.DHT11
    DHT_PIN = 4
    rh_now, suhu_now = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if rh_now is not None:
        kelembaban = rh_now
    if suhu_now is not None:
        suhu = suhu_now
    
 

    rc_time(pin_to_circuit, suhu, kelembaban)

    value_1 = hitung
    value_2 = suhu
    value_3 = kelembaban
    
    lat = -7.108717
    lng = 106.878470
    

   

    payload = {pin_to_circuit: value_1,
               varia_2: value_2,
               varia_3: value_3,
               varia_4: {"value": 1, "context": {"lat": lat, "lng": lng}}}

    return payload


   


def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True


def main():
    payload = build_payload(
        VARIABLE_LABEL_1, VARIABLE_LABEL_2, VARIABLE_LABEL_3, VARIABLE_LABEL_4)

    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")


def rc_time (pin_to_circuit, suhu, kelembaban):
    resist = 0
    duty = 2
    
    
   
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(2)




   
    GPIO.setup(pin_to_circuit, GPIO.IN)
  
   
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        resist += 1
    

  #  rh_now = 0
  #  suhu_now = 0
  #  DHT_SENSOR = Adafruit_DHT.DHT11
  #  DHT_PIN = 4
  #  rh, suhu = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
  #  if rh is not None:
  #     rh_now = rh
  # if suhu is not None:
  #     suhu_now = suhu


    
    
    if (resist > 0 and resist < 600) and (kelembaban  >= 70) and (suhu <=26): #Siang, Kelembaban tinggi, suhu rendah
        print("KONDISI PERTAMA SESUAI, GORDEN TERBUKA")

        servo1.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(0)
        time.sleep(0.01)
        servo1.ChangeDutyCycle(duty)
        servo2.ChangeDutyCycle(12)
        time.sleep(1)
        servo1.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(0)
        
       


    elif (resist > 0 and resist < 600) and (kelembaban <= 70) and (suhu >= 27) : 
        print("KONDISI KEDUA SESUAI, GORDEN DITUTUP")
        servo1.ChangeDutyCycle(duty)
        servo2.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(12)
    
    elif (resist > 600 ) and (kelembaban  >= 70) and (suhu <=26): # Malam, kelembaban tinggi, dan suhu rendah
        print("KONDISI KETIGA SESUAI, GORDEN TERTUTUP")
       
        servo1.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(0)
        time.sleep(0.01)
        servo1.ChangeDutyCycle(12)
        servo2.ChangeDutyCycle(duty)
        time.sleep(1)
        servo1.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(0)



    elif (resist > 600 ) and (kelembaban <= 70) and (suhu >= 27): 
        print("KONDISI KEEMPAT SESUAI, GORDEN DIBUKA")
       
        servo1.ChangeDutyCycle(12)
        servo2.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(duty)

    


if __name__ == '__main__':
    while (True):
        main()
        time.sleep(1)



  
