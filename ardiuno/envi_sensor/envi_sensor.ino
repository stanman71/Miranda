#include <FS.h>                   
#include <ESP8266WiFi.h>          
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>          
#include <ArduinoJson.h>     
#include <PubSubClient.h>     
#include "DHT.h"

// RESET 
int PIN_RESET_SETTING = 15;

// DHT Sensor
#define DHTPIN 0  
#define DHTTYPE DHT11   
DHT dht(DHTPIN, DHTTYPE);   

// Light Sensor
#define LIGHTPIN A0  

// MQTT
char mqtt_server[40];
char ieeeAddr[40];
char path[100];

WiFiClient espClient;
PubSubClient client(espClient);

// wifi manager
bool shouldSaveConfig = false;   


// ############
// split string
// ############

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


// ############
// wifi manager
// ############

void saveConfigCallback () {
    Serial.println("save new config...");
    shouldSaveConfig = true;
}

void wifi_manager(boolean reset_setting) {

    WiFiManager wifiManager;

    // reset settings ?
    if (reset_setting == true) {
        wifiManager.resetSettings();     // reset wifi settings
        SPIFFS.format();                 // reset config.txt
    }    

    // mounting filesystem
    
    Serial.print("mounting FS...");
  
    if (SPIFFS.begin()) {    
      
        Serial.println("successful");

        // read config file
        
        if (SPIFFS.exists("/config.json")) {
            Serial.print("reading config file...");
            File config_File = SPIFFS.open("/config.json", "r");

            if (config_File) {
              
                size_t size = config_File.size();
                std::unique_ptr<char[]> buf(new char[size]);
                config_File.readBytes(buf.get(), size);
                
                DynamicJsonDocument config_json(128);
                DeserializationError error = deserializeJson(config_json, buf.get());
                
                if (!error) {
                    strcpy(mqtt_server, config_json["mqtt_server"]);
                    Serial.println("successful");
          
                } else {
                    Serial.println("failed");
                }
                config_File.close();
            } 
        }
        
    } else {
        Serial.println("failed");
    }

    WiFiManagerParameter custom_mqtt_server("server", "mqtt server", mqtt_server, 40);

    wifiManager.setSaveConfigCallback(saveConfigCallback);
    wifiManager.addParameter(&custom_mqtt_server);

    if (!wifiManager.autoConnect("AutoConnectAP", "password")) {
        Serial.println("failed to connect and hit timeout");
        delay(3000);
        ESP.reset();
        delay(5000);
    }
  
    strcpy(mqtt_server, custom_mqtt_server.getValue());

    // save new config

    if (shouldSaveConfig) {
        
        DynamicJsonDocument json_data(128);
        json_data["mqtt_server"] = mqtt_server;
    
        File configFile = SPIFFS.open("/config.json", "w");
        
        if (!configFile) {
            Serial.println("failed to open config file for writing");
        }
        
        serializeJson(json_data, Serial);
        Serial.println();
        serializeJson(json_data, configFile);
        configFile.close();
        Serial.println("new config file saved");
    }
}


// ########
// ieeeAddr
// ########

void get_ieeeAddr() {
    Serial.print("mounting FS...");
  
    if (SPIFFS.begin()) {    
      
        Serial.println("successful");

        // read ieeeAddr file
        
        if (SPIFFS.exists("/ieeeAddr.json")) {
            Serial.print("reading ieeeAddr file...");
            File ieeeAddr_File = SPIFFS.open("/ieeeAddr.json", "r");

            if (ieeeAddr_File) {
                size_t size = ieeeAddr_File.size();
                std::unique_ptr<char[]> buf(new char[size]);
                ieeeAddr_File.readBytes(buf.get(), size);
                
                DynamicJsonDocument ieeeAddr_json(128);
                DeserializationError error = deserializeJson(ieeeAddr_json, buf.get());
                
                if (!error) {
                    strcpy(ieeeAddr, ieeeAddr_json["ieeeAddr"]);
                    Serial.println("successful");
          
                } else {
                    Serial.println("failed");
                }
                ieeeAddr_File.close();
            } 

        // ieeeAddr file not exist, generate new ieeeAddr + file
            
        } else {

            Serial.print("generate new ieeeAddr...");

            int randNumber            = random(100000, 999999);
            String ieeeAddr_generated = "0x" + String(randNumber); 
            
            ieeeAddr_generated.toCharArray(ieeeAddr,40); 

            DynamicJsonDocument ieeeAddr_json(128);
            ieeeAddr_json["ieeeAddr"] = ieeeAddr_generated;
        
            File ieeeAddr_File = SPIFFS.open("/ieeeAddr.json", "w");
            
            if (!ieeeAddr_File) {
                Serial.println("failed to open ieeeAddr file for writing");
            }
    
            serializeJson(ieeeAddr_json, Serial);
            Serial.println();
            serializeJson(ieeeAddr_json, ieeeAddr_File);
            ieeeAddr_File.close();
            Serial.println("new ieeeAddr file saved");
        }

    } else {
        Serial.println("failed");
    }
}


// ###########
// MQTT server
// ###########

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


// #############
// MQTT messages
// #############

void callback(char* topic, byte* payload, unsigned int length) {

    Serial.print("Incoming Message: ");
    Serial.println(topic); 

    String check_ieeeAddr = getValue(topic,'/',2);
    String check_command  = getValue(topic,'/',3);

    if(check_ieeeAddr == "devices"){

        // create path   
        String payload_path = "SmartHome/mqtt/log";
        char attributes_path[100];
        payload_path.toCharArray( path, 100 );    

        // create msg as json
        DynamicJsonDocument msg(256);
        
        msg["ieeeAddr"]    = ieeeAddr;
        msg["model"]       = "envi_sensor";
        msg["device_type"] = "sensor_passiv";
        msg["description"] = "MQTT Environment Sensor";
    
        JsonArray data_inputs = msg.createNestedArray("input_values");
        data_inputs.add("temperature");
        data_inputs.add("humidity");
        data_inputs.add("light");

        JsonArray data_events   = msg.createNestedArray("input_events");    
        JsonArray data_commands = msg.createNestedArray("commands");
        
        data_commands.add("");

        // convert msg to char
        char msg_Char[256];
        serializeJson(msg, msg_Char);
       
        Serial.print("Channel: ");
        Serial.println(path);        
        Serial.print("Publish message: ");
        Serial.println(msg_Char);
        Serial.println();   
             
        client.publish(path, msg_Char);        
    }

    if(check_ieeeAddr == ieeeAddr and check_command == "get"){
        send_default_mqtt_message();
    }    
}

// ####################
// MQTT default message
// ####################

void send_default_mqtt_message() {

    // create channelpath   
    String payload_path = "SmartHome/mqtt/" + String(ieeeAddr);
    char attributes_path[100];
    payload_path.toCharArray( path, 100 );      

    // create msg as json
    DynamicJsonDocument msg(128);
        
    float temperature = dht.readTemperature(); 
    float humidity    = dht.readHumidity();
    int light         = analogRead(LIGHTPIN);
    
    msg["temperature"] = temperature;
    msg["humidity"]    = humidity;
    msg["light"]       = light;
    
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


// #####
// setup
// #####

void setup() {
    Serial.begin(115200);
    Serial.println();

    pinMode(BUILTIN_LED, OUTPUT); 
    pinMode(PIN_RESET_SETTING,INPUT);

    digitalWrite(BUILTIN_LED, HIGH);
    
    dht.begin();    

    //if (digitalRead(PIN_RESET_SETTING) == 1) {
    //    wifi_manager(true);  // reset settings
    //} else {
    //    wifi_manager(false);
    //}
  
    wifi_manager(false);
    Serial.println(mqtt_server);

    get_ieeeAddr();
    Serial.println(ieeeAddr);
    
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

    client.loop();
}
