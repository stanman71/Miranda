#include <MCP3008.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
 
const char* SSID = "";
const char* PSK = "";
const char* MQTT_BROKER = "192.168.1.40";

// mqtt connection
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

// define pins mcp3008
#define CS_PIN 15
#define CLOCK_PIN 14
#define MOSI_PIN 13
#define MISO_PIN 12

MCP3008 adc(CLOCK_PIN, MOSI_PIN, MISO_PIN, CS_PIN);

// define pins transitor
int Pin_D0 = 16;
int Pin_D1 = 5;
int Pin_D2 = 4;
int Pin_D3 = 0;

// split string
String getValue(String data, char separator, int index)
    {
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

void setup() {
    pinMode(CS_PIN, OUTPUT);  
    pinMode(Pin_D0,OUTPUT);
    pinMode(Pin_D1,OUTPUT);
    pinMode(Pin_D2,OUTPUT);
    pinMode(Pin_D3,OUTPUT);
    
    Serial.begin(115200);
    setup_wifi();
    client.setServer(MQTT_BROKER, 1883);
    client.setCallback(callback);

    digitalWrite(Pin_D3, HIGH);
}

void setup_wifi() {
    delay(10);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(SSID);
 
    WiFi.begin(SSID, PSK);
 
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
 
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("[");    
    Serial.print(topic);
    Serial.print("] ");
    char msg[length+1];
  
    for (int i = 0; i < length; i++) {
        Serial.print((char)payload[i]);
        msg[i] = (char)payload[i];
        }
   
    Serial.println();
    msg[length] = '\0';

    String check_target = getValue(topic,'/',3);

    if(check_target == "device"){
        Serial.print("Publish message: ");
        client.publish("/SmartHome/watering_array_v4/deviceinformation", "watering_array_v4/8/4");        
        }

    if(check_target == "plant"){
        // get plant_id
        String STR_plant_id = getValue(topic,'/',4);
        // get sensor_id
        int sensor_id = atoi(msg);

        // get sensor_value
        int sensorValue = adc.readADC(sensor_id); 
        String STR_value = String(sensorValue);

        // create msg   
        String payload = STR_plant_id + "/" + STR_value;      
        char attributes[100];
        payload.toCharArray( msg, 100 );

        Serial.print("Publish message: ");
        Serial.print("[/SmartHome/sensor/plant] ");
        Serial.print(msg);
        Serial.println();
        client.publish("/SmartHome/data/plant", msg);         
        }    

    if(check_target == "sensor"){
        // get file
        String STR_file = getValue(topic,'/',4);
        // get sensor_id
        int sensor_id = atoi(msg);

        // get sensor_value
        int sensorValue = adc.readADC(sensor_id);   
        String STR_value = String(sensorValue);

        // create msg   
        String payload = STR_file + "/" + STR_value;      
        char attributes[100];
        payload.toCharArray( msg, 100 );

        Serial.print("Publish message: ");
        Serial.print("[/SmartHome/sensor/sensor] ");
        Serial.print(msg);
        Serial.println();
        client.publish("/SmartHome/data/sensor", msg);         
        }    

     if(check_target == "pump"){
        // get pump_id
        String STR_pump_id = getValue(topic,'/',4); 
        String STR_msg = msg;  

        if (STR_pump_id == "0") {
            if (STR_msg == "on") {
                digitalWrite(Pin_D0, HIGH);
                Serial.println("Start_Pump_0");
            }
            else {
                digitalWrite(Pin_D0, LOW); 
                Serial.println("Stop_Pump_0");
            }
        }
        if (STR_pump_id == "1") {
            if (STR_msg == "on") {
                digitalWrite(Pin_D3, HIGH);
                Serial.println("Start_Pump_1");
            }
            else {
                digitalWrite(Pin_D3, LOW); 
                Serial.println("Stop_Pump_1");
            }
        }     
        if (STR_pump_id == "2") {
            if (STR_msg == "on") {
                digitalWrite(Pin_D2, HIGH);
                Serial.println("Start_Pump_2");
            }
            else {
                digitalWrite(Pin_D2, LOW); 
                Serial.println("Stop_Pump_2");
            }
        }
        if (STR_pump_id == "3") {
            if (STR_msg == "on") {
                digitalWrite(Pin_D1, HIGH);
                Serial.println("Start_Pump_3");
            }
            else {
                digitalWrite(Pin_D1, LOW); 
                Serial.println("Stop_Pump_3");
            }
        }
     }
}

void reconnect() {
    while (!client.connected()) {
        Serial.print("Reconnecting...");
        if (!client.connect("ESP8266Client")) {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" retrying in 5 seconds");
            delay(5000);
        }
    }
    client.subscribe("/SmartHome/watering_array_v4/#");
    Serial.println("MQTT Connected...");
}

void loop() {

    if (!client.connected()) {
        reconnect();
    }
    client.loop();
}
