#mein Heizstab PWM Programm
import time
import RPi.GPIO as GPIO
import requests
import json

ledpin = 13
minleistung_pv = 400 #minimaler Überschuss in W
leistung_heizstab = 3000 #Heizstableistung in W

GPIO.setmode(GPIO.BCM)
GPIO.setup(ledpin, GPIO.OUT)
 
p = GPIO.PWM(ledpin, 2000)  # frequency=50Hz
p.start(0)
p.ChangeDutyCycle(0)

link_efriendsmeter = "https://xyz.balena-devices.com/api/MeterData/getCurrentValue"
# p.stop()
# GPIO.cleanup()
# raise SystemExit

try:
    while 1:
        try:
            f = requests.get(link_efriendsmeter)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print('connection error')
            time.sleep(30)
            continue
        # print(f.text)
        #echte Response
        efdata = json.loads(f.text)
        #falsche Response testen
        # efdata = json.loads("{}")
        #korrekt Response testen
        # efdata = json.loads('{"endTime": "2022-07-21T18:46:20.000Z", "startTime": "2022-07-21T18:46:10.000Z", "energyBalance": 578.8}')

        #sicherheitshalber abschalten
        heizstabvalue = 0
        if "energyBalance" in efdata:
            if efdata['energyBalance'] > minleistung_pv:
                #energy beinhaltet den Überschusswert z.B. 1200 W
                energy = efdata['energyBalance']
                if energy > leistung_heizstab: energy = leistung_heizstab
                heizstabvalue = energy * 100 / leistung_heizstab
                print('Prozent Leistung: ', heizstabvalue)
            else:
                print('energyBalance to low ', efdata['energyBalance'])
        else:
            print('nodata')
        #richtiger Code
        p.ChangeDutyCycle(heizstabvalue)
        # alle 10sek einlesen
        time.sleep(10)


except KeyboardInterrupt:
    pass
    p.stop()
    GPIO.cleanup()



