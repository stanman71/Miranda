#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

String ieeeAddr = "0x99999";

const char* ssid        = "Stanlay"; 
const char* password    = "G3f!7jak5$U9H4K7/G6"; 
const char* mqtt_server = "192.168.1.40";

char path[100];

// mqtt connection
WiFiClient espClient;
PubSubClient client(espClient);

// INPUT
int PIN_ANALOG  = A0;
int PIN_DIGITAL = 14;

// OUTPUT 
int PIN_PUMP      = 15;
int PIN_LED_GREEN = 12;
int PIN_LED_RED   = 13;


// ############
// split string
// ############

String getValue(String data, char separator, int index) {
  
    int found = 0;
    int strIndex[] = {0, -1};
    int maxIndex = data.length()-1;
  
    for (int i=0; i<=maxIndex && found<=index; i++){
        if(data.charAt(i)==separator || i==maxIndex){
            found++;
            strIndex[0] = strIndex[1]+1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    } 
    return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}


// #######################
// mqtt response functions 
// #######################

void callback (char* topic, byte* payload, unsigned int length) {

    Serial.print("Incoming Message: ");
    Serial.println(topic); 

    String check_ieeeAddr = getValue(topic,'/',2);
    String check_command  = getValue(topic,'/',3);

    // devices 
    if (check_ieeeAddr == "devices"){

        // create path   
        String payload_path = "SmartHome/mqtt/log";
        char attributes_path[100];
        payload_path.toCharArray( path, 100 );    

        // create msg as json
        DynamicJsonDocument msg(512);
        
        msg["ieeeAddr"]    = ieeeAddr;
        msg["model"]       = "watering_array_v1";
        msg["device_type"] = "watering_control";
        msg["description"] = "MQTT Watering_Array";
    
        JsonArray data_inputs = msg.createNestedArray("input_values");
        data_inputs.add("pump");
        data_inputs.add("pump_time");        
        data_inputs.add("sensor_moisture");
        data_inputs.add("sensor_watertank");        

        JsonArray data_events = msg.createNestedArray("input_events");
        
        JsonArray data_commands = msg.createNestedArray("commands");
        data_commands.add("{'pump':'ON','pump_time':15}");     
        data_commands.add("{'pump':'ON','pump_time':30}");             
        data_commands.add("{'pump':'ON','pump_time':45}");     
        data_commands.add("{'pump':'ON','pump_time':60}");  
        data_commands.add("{'pump':'ON'}");              
        data_commands.add("{'pump':'OFF'}");   

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

    // get 
    if (check_ieeeAddr == ieeeAddr and check_command == "get"){
        send_default_mqtt_message(0);    
    }    


    // set 
    if (check_ieeeAddr == ieeeAddr and check_command == "set"){

        char msg[length+1];
  
        for (int i = 0; i < length; i++) {
            msg[i] = (char)payload[i];
        }
        msg[length] = '\0';
        
        Serial.print("msg: ");
        Serial.println(msg);

        // convert msg to json
        DynamicJsonDocument msg_json(128);
        deserializeJson(msg_json, msg);
    
        String pump_setting  = msg_json["pump"];
        int pumptime         = msg_json["pump_time"];

        // control pump automatically  
        if (pump_setting == "ON" and pumptime != 0) {

            digitalWrite(PIN_PUMP, HIGH);

            send_default_mqtt_message(pumptime);
            
            Serial.println("PUMP_ON");

            delay(pumptime * 1000);
            
            // #########
            // stop pump
            // #########
            
            digitalWrite(PIN_PUMP, LOW);
     
            while (!client.connected()) {
                reconnect();
            }
            
            send_default_mqtt_message(0);
            Serial.println("PUMP_OFF");                               
        }

        // start pump manually    
        if (pump_setting == "ON" and pumptime == 0) {

            digitalWrite(PIN_PUMP, HIGH);
     
            while (!client.connected()) {
                reconnect();
            }
            
            send_default_mqtt_message(0);
            Serial.println("PUMP_ON");                                
        }

        // stop pump manually    
        if (pump_setting == "OFF") {

            digitalWrite(PIN_PUMP, LOW);
     
            while (!client.connected()) {
                reconnect();
            }
            
            send_default_mqtt_message(0);
            Serial.println("PUMP_OFF");                                
        }
    }     
}


// ####################
// mqtt default message
// ####################

void send_default_mqtt_message(int pumptime_value) {

    // create channel  
    String payload_path = "SmartHome/mqtt/" + String(ieeeAddr);     
    char attributes[100];
    payload_path.toCharArray( path, 100 );    
 
    // create msg as json
    DynamicJsonDocument msg(128);

    // get pump state
    if (digitalRead(PIN_PUMP) == 1) { 
      
        msg["pump"] = "ON";
        
    } else { 
      
        msg["pump"] = "OFF";
    }

    msg["pump_time"] = pumptime_value;

    // get sensor data
    int sensor_moisture  = analogRead(PIN_ANALOG);
    int sensor_watertank = digitalRead(PIN_DIGITAL);

    msg["sensor_moisture"]  = sensor_moisture;
    msg["sensor_watertank"] = sensor_watertank;

    // convert msg to char
    char msg_Char[128];
    serializeJson(msg, msg_Char);

    Serial.print("Channel: ");
    Serial.println(path);
    Serial.print("Publish message: ");
    Serial.println(msg_Char);
    Serial.println();
    
    client.publish(path, msg_Char);    
}


// ###############
// mqtt connection
// ###############

void reconnect() {
    while (!client.connected()) {
 
        Serial.print("MQTT: ");       
        Serial.print("Connecting...");

        String clientId = "ESP8266Client-";
        clientId += String(random(0xffff), HEX);

        digitalWrite(BUILTIN_LED, HIGH);

        if (client.connect(clientId.c_str())) { 
  
            send_default_mqtt_message(0);

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


// ##########
// setup wifi
// ##########

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


// #####
// setup
// #####

void setup() {

    Serial.begin(115200);
    
    pinMode(PIN_DIGITAL,INPUT);
    pinMode(PIN_PUMP,OUTPUT);
    pinMode(PIN_LED_RED,OUTPUT);
    pinMode(PIN_LED_GREEN,OUTPUT);
    pinMode(BUILTIN_LED, OUTPUT); 
 
    digitalWrite(PIN_PUMP, LOW); 

    setup_wifi();
    client.setServer(mqtt_server, 1883);
    client.setCallback(callback); 
}


// ####
// loop
// ####

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
