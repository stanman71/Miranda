extern "C" {
  #include "user_interface.h"
}

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include <ESP8266HTTPClient.h>
#include <ESP8266httpUpdate.h>

String ieeeAddr = "0x99999";

const int FW_VERSION  = 1000;
const char* fwUrlBase = "http://192.168.1.40/firmware/watering_control/0x99999";

const char* ssid        = ""; 
const char* password    = ""; 
const char* mqtt_server = "";

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


// ###############
// firmware update 
// ###############

void checkForUpdates() {
  
    String mac = getMAC();
    String fwURL = String( fwUrlBase );
    fwURL.concat( mac );
    String fwVersionURL = fwURL;
    fwVersionURL.concat( ".version" );
  
    Serial.println( "Checking for firmware updates." );
    Serial.print( "MAC address: " );
    Serial.println( mac );
    Serial.print( "Firmware version URL: " );
    Serial.println( fwVersionURL );
  
    HTTPClient httpClient;
    httpClient.begin( fwVersionURL );
    int httpCode = httpClient.GET();
    
    if ( httpCode == 200 ) {
      
        String newFWVersion = httpClient.getString();
    
        Serial.print( "Current firmware version: " );
        Serial.println( FW_VERSION );
        Serial.print( "Available firmware version: " );
        Serial.println( newFWVersion );
    
        int newVersion = newFWVersion.toInt();
    
        if ( newVersion > FW_VERSION ) {
          
            Serial.println( "Preparing to update" );
      
            String fwImageURL = fwURL;
            fwImageURL.concat( ".bin" );
            t_httpUpdate_return ret = ESPhttpUpdate.update( fwImageURL );
      
            switch(ret) {
                case HTTP_UPDATE_FAILED:
                  Serial.printf("HTTP_UPDATE_FAILD Error (%d): %s", ESPhttpUpdate.getLastError(), ESPhttpUpdate.getLastErrorString().c_str());
                  break;
        
                case HTTP_UPDATE_NO_UPDATES:
                  Serial.println("HTTP_UPDATE_NO_UPDATES");
                  break;
            }
        }
        
        else {
           Serial.println( "Already on latest version" ); 
        }
    }
    
    else {
        Serial.print( "Firmware version check failed, got HTTP response code " );
        Serial.println( httpCode );
    }
    
    httpClient.end();
}

String getMAC() {
  
    uint8_t mac[6];
    char result[14];
  
    snprintf( result, sizeof( result ), "%02x%02x%02x%02x%02x%02x", mac[ 0 ], mac[ 1 ], mac[ 2 ], mac[ 3 ], mac[ 4 ], mac[ 5 ] );
  
    return String( result );
}


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
        data_inputs.add("pump_state");
        data_inputs.add("sensor_moisture");
        data_inputs.add("sensor_watertank");
        data_inputs.add("firmware");        

        JsonArray data_events = msg.createNestedArray("input_events");
        
        JsonArray data_commands = msg.createNestedArray("commands");
        data_commands.add("{'pump_state':'ON'}");     
        data_commands.add("{'pump_state':'OFF'}");

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
        send_default_mqtt_message();    
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
        DynamicJsonDocument msg_json(64);
        deserializeJson(msg_json, msg);
    
        String pump_setting  = msg_json["pump_state"];
        int pumptime         = msg_json["pump_time"];
        pumptime             = pumptime * 1000; 


        // start pump automatically   
        if (pump_setting == "ON" and pumptime != 0) {

            digitalWrite(PIN_PUMP, HIGH);

            send_default_mqtt_message();
            
            Serial.println("PUMP_ON");

            delay(pumptime);
            
            // #########
            // stop pump
            // #########
            
            digitalWrite(PIN_PUMP, LOW);
     
            while (!client.connected()) {
                reconnect();
            }
            
            send_default_mqtt_message();
            Serial.println("PUMP_OFF");                               
        }


        // start pump manually
        if (pump_setting == "ON" and pumptime == 0) {
            
            digitalWrite(PIN_PUMP, HIGH);
            
            send_default_mqtt_message();
            Serial.println("PUMP_ON");                        
        }        


        // stop pump manually    
        if (pump_setting == "OFF") {

            digitalWrite(PIN_PUMP, LOW);
     
            while (!client.connected()) {
                reconnect();
            }
            
            send_default_mqtt_message();
            Serial.println("PUMP_OFF");                                
        }
    }     
}


// ####################
// mqtt default message
// ####################

void send_default_mqtt_message() {

    // create channel  
    String payload_path = "SmartHome/mqtt/" + ieeeAddr;      
    char attributes[100];
    payload_path.toCharArray( path, 100 );    

  
    // create msg as json
    DynamicJsonDocument msg(128);

    // get pump state
    if (digitalRead(PIN_PUMP) == 1) { 
      
        msg["pump_state"] = "ON";
        
    } else { 
      
        msg["pump_state"] = "OFF";
    }

    // get sensor data
    int sensor_moisture  = analogRead(PIN_ANALOG);
    int sensor_watertank = digitalRead(PIN_DIGITAL);

    msg["sensor_moisture"]  = sensor_moisture;
    msg["sensor_watertank"] = sensor_watertank;
    msg["firmware"]         = FW_VERSION;

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
  
            send_default_mqtt_message();

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


// #####
// setup
// #####

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

void setup() {

    Serial.begin(115200);
    
    pinMode(PIN_DIGITAL,INPUT);
    pinMode(PIN_PUMP,OUTPUT);
    pinMode(PIN_LED_RED,OUTPUT);
    pinMode(PIN_LED_GREEN,OUTPUT);
    pinMode(BUILTIN_LED, OUTPUT); 

    digitalWrite(PIN_PUMP, LOW); 

    setup_wifi();
    checkForUpdates();
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
