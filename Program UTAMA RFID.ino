//Program Utama Project RFID Kandang Sapi
//Laboratorium Teknik Manufaktur Teknik Industri Universitas Brawijaya
//Author : Lab. Elektronika Universitas Brawijaya
//Ver : 1.0
//Release Date : 15-05-2019

#include <Arduino.h>
#include <MFRC522.h> //library untuk RFID reader
#include <SPI.h> //library untuk komunikasi SPI
#include <WiFi.h>//Library untuk wifi 
#include <Wire.h>
#include <PubSubClient.h>

#define SS_PIN 21
#define RST_PIN 22
#define LEDMERAH  4
#define LEDHIJAU  0
#define LEDBIRU   2

#define WIFI_SSID       "YourSSID" //change to your WiFi SSID
#define WIFI_PASSWORD   "YourPassword" //change to your WiFi Password

#define MQTT_HOST       "maqiatto.com"
#define MQTT_PORT       1883 //change to your MQTT port
#define MQTT_USERNAME   "YourUsername" //change to your MQTT username
#define MQTT_KEY        "YourKey" //change to your MQTT key

#define TOPIC           "YourTopic" //change to your topic

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);


boolean MQTTPublish(const char* topic, char* payload);

MFRC522 rfid(SS_PIN, RST_PIN);

byte nuidPICC[4];
String ID="";

boolean adaKartu = false;

void setup() {
    pinMode(2, OUTPUT);
    pinMode(LEDMERAH, OUTPUT);
    pinMode(LEDHIJAU, OUTPUT);
    digitalWrite(LEDHIJAU, HIGH); //HIGH akan membuat LED Mati
    digitalWrite(LEDBIRU, HIGH);
    digitalWrite(LEDMERAH, HIGH);
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED){
    delay(200);
    digitalWrite(LEDMERAH, LOW);
    delay(200);
    digitalWrite(LEDMERAH, HIGH);
    Serial.println("Nyambungin ke WiFi dulu coy...");
  }
  digitalWrite(LEDHIJAU, LOW);
  delay(2500);
  Serial.println("Udah terhubung nih");
  SPI.begin(); //Inisialisasi SPI bus
  rfid.PCD_Init();
  Serial.println(WiFi.localIP());
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  

}

void loop() {
    if(!mqttClient.connected()){
    while(!mqttClient.connected()){
        if(mqttClient.connect("", MQTT_USERNAME, MQTT_KEY)){
          Serial.println("Connected to MQTT Server");
        }
        else{
          Serial.println("Tidak Connect");
        }
      }
    }
    digitalWrite(LEDHIJAU,HIGH);
    adaKartu = status_rfid();
    if(adaKartu == true){
      ID = getID();
      int str_len = ID.length()+1;
      char ID_array[str_len];
      ID.toCharArray(ID_array, str_len);
      digitalWrite(LEDBIRU, LOW);
      delay(500);
      digitalWrite(LEDBIRU,HIGH);
      if(MQTTPublish(TOPIC, ID_array)){   //ganti "12345678" dengan ID RFID
        Serial.println("Sukses mengirim ke Broker");
        Serial.println(ID_array);
      }
      adaKartu = false;
    }
  while (WiFi.status() != WL_CONNECTED){
    delay(200);
    digitalWrite(LEDMERAH, LOW);
    delay(200);
    digitalWrite(LEDMERAH, HIGH);
    Serial.println("Koneksi terputus");
    if(WiFi.status() == WL_CONNECTED){
      digitalWrite(LEDHIJAU, LOW);
      delay(2500);
      digitalWrite(LEDHIJAU, HIGH);
    }
  }
  
}

boolean status_rfid(){
   if (!rfid.PICC_IsNewCardPresent()) 
  {
    return 0;
  } 
  if(!rfid.PICC_ReadCardSerial())
  {
    return 0;  
  }
  return 1; 
}

String getID(){
    ID = "";
    for (byte i = 0; i < 4; i++) {
      nuidPICC[i] = rfid.uid.uidByte[i];
      ID.concat(String(rfid.uid.uidByte[i], HEX));
    }
    ID.toUpperCase(); 
    Serial.println(ID);
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
    return ID;
}

boolean MQTTPublish(const char* topic, char* payload)
{
  boolean retval = false;
  if (mqttClient.connected())
  {
    retval = mqttClient.publish(topic, payload);
  }
  return retval;
}

