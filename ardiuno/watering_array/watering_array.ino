#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

String ieeeAddr = "0x99999";

const char* ssid        = ""; 
const char* password    = ""; 
const char* mqtt_server = "";

// mqtt connection
WiFiClient espClient;
PubSubClient client(espClient);
char path[50];
int value = 0;

// INPUT
int PIN_ANALOG = A0;
int PIN_DIGITAL = 14;

// OUTPUT 
int PIN_PUMP = 0;
int PIN_LED_GREEN = 12;
int PIN_LED_RED = 13;

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
        msg["model"]       = "watering_array_v1";
        msg["device_type"] = "watering_array";
        msg["description"] = "MQTT Watering_Array";
    
        JsonArray data_inputs = msg.createNestedArray("inputs");
        data_inputs.add("sensor_0");
        data_inputs.add("sensor_1");

        JsonArray data_commands = msg.createNestedArray("commands");
        data_commands.add("PUMP_ON");
        data_commands.add("PUMP_OFF");

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

        // create path   
        String payload_path = "SmartHome/mqtt/" + ieeeAddr;
        char attributes_path[100];
        payload_path.toCharArray( path, 100 );   

        int sensor_0 = analogRead(PIN_ANALOG);
        int sensor_1 = digitalRead(PIN_DIGITAL);

        // create msg as json
        DynamicJsonDocument msg(1024);
        
        msg["sensor_0"] = sensor_0;
        msg["sensor_1"] = sensor_1;

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

    if(check_ieeeAddr == ieeeAddr and check_command == "set"){

        // create path   
        String payload_path = "SmartHome/mqtt/" + ieeeAddr;
        char attributes_path[100];
        payload_path.toCharArray( path, 100 );    

        char msg[length+1];
  
        for (int i = 0; i < length; i++) {
            msg[i] = (char)payload[i];
        }
        msg[length] = '\0';
        
        Serial.print("msg: ");
        Serial.println(msg);

        // convert msg to json
        DynamicJsonDocument msg_json(50);
        deserializeJson(msg_json, msg);
        
        String pump_setting = msg_json["state"];      

        if (pump_setting == "PUMP_ON") {
            digitalWrite(PIN_PUMP, HIGH);

            // create msg as json
            DynamicJsonDocument msg(50);     
            msg["state"] = "PUMP_ON";

            // convert msg to char
            char msg_Char[50];
            serializeJson(msg, msg_Char);
            
            client.publish(path, msg_Char);
            Serial.println("PUMP_ON");
        }
        if (pump_setting == "PUMP_OFF") {
            digitalWrite(PIN_PUMP, LOW); 

            // create msg as json
            DynamicJsonDocument msg(50);     
            msg["state"] = "PUMP_OFF";

            // convert msg to char
            char msg_Char[50];
            serializeJson(msg, msg_Char);
            
            client.publish(path, msg_Char);
            Serial.println("PUMP_OFF");
        }   
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

    pinMode(PIN_DIGITAL,INPUT);
    pinMode(PIN_PUMP,OUTPUT);
    pinMode(PIN_LED_RED,OUTPUT);
    pinMode(PIN_LED_GREEN,OUTPUT);
    pinMode(BUILTIN_LED, OUTPUT); 
}

void loop() {

    if (!client.connected()) {
        reconnect();
    }
    
    int sensor_1 = digitalRead(PIN_DIGITAL);

    if (sensor_1 == 0) {
      digitalWrite(PIN_LED_RED, HIGH);
      digitalWrite(PIN_LED_GREEN, LOW);
    }

    if (sensor_1 == 1) {
      digitalWrite(PIN_LED_RED, LOW);
      digitalWrite(PIN_LED_GREEN, HIGH);
    }
    
    delay(100);
    client.loop();
}