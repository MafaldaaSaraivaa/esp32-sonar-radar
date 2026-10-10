#include <Arduino.h>
#include <WiFi.h>
#include <ESP32Servo.h>
#include "secrets.h"

const int servoPin = 19;    //Pin where the microservo is connected
const int TrigPin = 5;      //Trigger pin for the HC-SR04
const int EchoPin = 18;     //Echo pin for the HC-SR04

const char* Wifi_Name = WIFI_SSID; // WiFi name
const char* Wifi_Password = WIFI_PASSWORD; //Wifi password

Servo servo; 

void setup() {
    Serial.begin(115200); 
    WiFi.begin(Wifi_Name, Wifi_Password);
    pinMode(TrigPin, OUTPUT);
    pinMode(EchoPin, INPUT);
    servo.attach(servoPin);

    while(WiFi.status() != WL_CONNECTED){
        delay(2000);
        Serial.print(WiFi.status());
    } 
}

long medirdistancia(){
    digitalWrite(TrigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(TrigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(TrigPin, LOW);

    long duracao = pulseIn(EchoPin, HIGH, 23529);

    long distancia = (duracao * 0.034) / 2;

    return distancia;
}

void loop() {

    for (int angulo = 0; angulo <= 180; angulo = angulo + 5){
        servo.write (angulo);
        delay(223);

        long d = medirdistancia();

        Serial.print(angulo);
        Serial.print(",");
        Serial.println(d);
    }

    for (int angulo = 179; angulo >= 0; angulo = angulo -5){
        servo.write (angulo);
        delay(223);

        long d = medirdistancia();

        Serial.print(angulo);
        Serial.print(",");
        Serial.println(d);
    }
}