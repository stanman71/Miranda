String ieeeAddr = "0x777777";

const char* ssid        = ""; 
const char* password    = ""; 
const char* mqtt_server = "";

#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// mqtt connection
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[300];
char path[50];
int value = 0;

// INPUT
int PIN_ANALOG = A0
int PIN_DIGITAL = 5;

// OUTPUT 
int PIN_PUMP = 4;

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
               
        // create msg  
        String payload_msg = "{\"ieeeAddr\":\"" + ieeeAddr + "\"," + 
                             "\"model\":\"watering_array_v1\"," +
                             "\"device_type\":\"watering_array\"," +
                             "\"description\":\"Watering with Sensors (1 Plant)\"," +
                             "\"inputs\":[\"sensor_0\",\"sensor_1\"]," +
                             "\"outputs\":[\"pump_0\"]}";   
                                           
        char attributes[300];
        payload_msg.toCharArray( msg, 300 );
        
        Serial.print("Channel: ");
        Serial.println(path);         
        Serial.print("Publish message: ");
        Serial.println(msg);
        Serial.println();      
          
        client.publish(path, msg);        
    }

    if(check_ieeeAddr == ieeeAddr and check_command == "get"){

        int sensor_0 = analogRead(PIN_ANALOG);
        int sensor_1 = digitalRead(PIN_DIGITAL);

        // create path   
        String payload_path = "SmartHome/mqtt/" + ieeeAddr;
        char attributes_path[100];
        payload_path.toCharArray( path, 100 );   

        // create msg   
        String payload_msg = "{\"sensor_0\":" + STR_sensor_0 + 
                             ",\"sensor_1\":" + STR_sensor_1 + "}";
        char attributes_msg[100];
        payload_msg.toCharArray(  msg, 200 );     

        Serial.print("Channel: ");
        Serial.println(path);
        Serial.print("Publish message: ");
        Serial.println(msg);
        Serial.println();
        
        client.publish(path, msg);         
    }    

    if(check_ieeeAddr == ieeeAddr and check_command == "set"){

        char msg[length+1];
  
        for (int i = 0; i < length; i++) {
            msg[i] = (char)payload[i];
        }
        msg[length] = '\0';
        
        Serial.print("msg: ");
        Serial.println(msg);

        // create path   
        String payload_path = "SmartHome/mqtt/" + ieeeAddr;
        char attributes_path[100];
        payload_path.toCharArray( path, 100 );          

        // get command
        String pump        = getValue(msg,':',0);      
        String pump_state  = getValue(msg,':',1); 
        
        if (pump_state == "on") {
            digitalWrite(PIN_PUMP, HIGH);
            client.publish(path, "pump_0:on");
            Serial.println("pump_0:on");
        }
        else {
            digitalWrite(PIN_PUMP, LOW); 
            client.publish(path, "pump_0:off");
            Serial.println("pump_0:off");
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
    pinMode(BUILTIN_LED, OUTPUT); 
    
}

void loop() {

    if (!client.connected()) {
        reconnect();
    }
    
    client.loop();
}
