String ieeeAddr = "0x88888";

const char* ssid        = ""; 
const char* password    = ""; 
const char* mqtt_server = "";

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

// mqtt connection
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[100];
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

        // create msg  
        String payload = "{\"ieeeAddr\":\"" + ieeeAddr + "\",\"model\":\"envi_sensor\"," +
                         "\"inputs\":[\"temperature\",\"humidity\",\"light\"],\"outputs\":0}";      
        char attributes[200];
        payload.toCharArray( msg, 200 );
        
        Serial.print("Publish message: ");
        Serial.println(msg);
        Serial.print("Channel: ");
        Serial.println("SmartHome/mqtt/log");
        Serial.println();        
        client.publish("SmartHome/mqtt/log", msg);        
    }

    if(check_ieeeAddr == ieeeAddr and check_command == "get"){
    
        float temperature = dht.readTemperature(); 
        String STR_temperature = String(temperature);
        float humidity = dht.readHumidity();
        String STR_humidity = String(humidity);
        int light = analogRead(LIGHTPIN);
        String STR_light = String(light);  

        // create msg   
        String payload_msg = "{\"temperature\":" + STR_temperature +        
                             ",\"humidity\":" + STR_humidity + 
                             ",\"light\":" + STR_light + "}";

        char attributes_msg[100];
        payload_msg.toCharArray( msg, 100 );

        // create channelpath   
        String payload_path = "SmartHome/mqtt/" + ieeeAddr;
        char attributes_path[100];
        payload_path.toCharArray( path, 100 );        

        Serial.print("Publish message: ");
        Serial.println(msg);
        Serial.print("Channel: ");
        Serial.println("SmartHome/mqtt/" + ieeeAddr);
        Serial.println();
        client.publish(path, msg);         
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
