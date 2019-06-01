#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"
#include <ArduinoJson.h>

String ieeeAddr = "0x88888";

const char* ssid        = ""; 
const char* password    = ""; 
const char* mqtt_server = "";

// mqtt connection
WiFiClient espClient;
PubSubClient client(espClient);
char path[50];
int value = 0;

// DHT Sensor
#define DHTPIN 0  
#define DHTTYPE DHT11   
DHT dht(DHTPIN, DHTTYPE);   

// Light Sensor
#define LIGHTPIN A0  

// split string
String getValue(String data, char separator, int index) {
    int found = 0;
    int strIndex[] = {0, -1};
    int maxIndex = data.length()-1;
  
    for(int i=0; i<=maxIndex && found<=index; i++){
        if(data.charAt(i)==separator || i==maxIndex){
            found++;
            strIndex[0] = strIndex[1]+1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    } 
    return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void setup_wifi() {
    delay(10);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
  
    WiFi.begin(ssid, password);
  
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
      }
  
    randomSeed(micros());
  
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {

    Serial.println("######################");
    Serial.print("Channel: ");
    Serial.println(topic);
    Serial.println("######################");

    String check_ieeeAddr = getValue(topic,'/',2);
    String check_command  = getValue(topic,'/',3);

    if(check_ieeeAddr == "devices"){

        // create path   
        String payload_path = "SmartHome/mqtt/log";
        char attributes_path[100];
        payload_path.toCharArray( path, 100 );    

        // create msg as json
        DynamicJsonDocument msg(1024);
        
        msg["ieeeAddr"]    = ieeeAddr;
        msg["model"]       = "envi_sensor";
        msg["device_type"] = "sensor_passiv";
        msg["description"] = "MQTT Environment Sensor";
    
        JsonArray data_inputs = msg.createNestedArray("inputs");
        data_inputs.add("temperature");
        data_inputs.add("humidity");
        data_inputs.add("light");

        JsonArray data_commands = msg.createNestedArray("commands");
        data_commands.add("");

        // convert msg to char
        char msg_Char[512];
        serializeJson(msg, msg_Char);
       
        Serial.print("Channel: ");
        Serial.println(path);        
        Serial.print("Publish message: ");
        Serial.println(msg_Char);
        Serial.println();   
             
        client.publish(path, msg_Char);        
    }

    if(check_ieeeAddr == ieeeAddr and check_command == "get"){

        // create channelpath   
        String payload_path = "SmartHome/mqtt/" + ieeeAddr;
        char attributes_path[100];
        payload_path.toCharArray( path, 100 );      
            
        float temperature = dht.readTemperature(); 
        float humidity    = dht.readHumidity();
        int light         = analogRead(LIGHTPIN);
  
        // create msg as json
        DynamicJsonDocument msg(1024);
        
        msg["temperature"] = temperature;
        msg["humidity"]    = humidity;
        msg["light"]       = light;
        
        // convert msg to char
        char msg_Char[100];
        serializeJson(msg, msg_Char);
        
        Serial.print("Channel: ");
        Serial.println(path);
        Serial.print("Publish message: ");
        Serial.println(msg_Char);
        Serial.println();
        
        client.publish(path, msg_Char);         
    }    
}

void reconnect() {
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        String clientId = "ESP8266Client-";
        clientId += String(random(0xffff), HEX);

        digitalWrite(BUILTIN_LED, HIGH);
        
        if (client.connect(clientId.c_str())) {     
            // create channel  
            String payload_path = "SmartHome/mqtt/" + ieeeAddr;      
            char attributes[100];
            payload_path.toCharArray( path, 100 );    
                 
            client.publish(path, "connected");
            client.subscribe("SmartHome/mqtt/#");
            Serial.println("MQTT Connected...");

            digitalWrite(BUILTIN_LED, LOW); 
          
        } else {        
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

void setup() {
    
    Serial.begin(115200);
    setup_wifi();
    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);

    pinMode(BUILTIN_LED, OUTPUT); 
    dht.begin();
}

void loop() {

    if (!client.connected()) {
        reconnect();
    }
    
    client.loop();
}
