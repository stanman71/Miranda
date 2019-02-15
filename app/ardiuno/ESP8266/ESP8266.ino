#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>

ESP8266WiFiMulti WiFiMulti;

void setup() 

    {
      Serial.begin(115200);

      // boot break (4s)
      for(uint8_t t = 4; t > 0; t--) 

          {
            Serial.printf("SETUP WAIT %d...\n", t);
            Serial.flush();
            delay(1000);
          }

      // SSID, Password
      WiFiMulti.addAP("Stanlay", ""); 
      
      //  Force the ESP into client-only mode
      WiFi.mode(WIFI_STA); 

    }


void loop() 

    {
   
      if((WiFiMulti.run() == WL_CONNECTED)) 

          {
            Serial.println("WiFi connected");

            // read sensor
            int sensorValue = analogRead(A0);
            float voltage = sensorValue * (3.2 / 1023.0);
            
            Serial.println(voltage);

            String voltage_result;
            voltage_result = String(voltage);

            // transfer values to the raspberry
            HTTPClient http;
            http.begin("http://192.168.1.40:5000/mqtt/0/sensor/" + voltage_result);
            int httpCode = http.GET();
            http.end();

            Serial.println("Going into deep sleep for 30 minutes");
            ESP.deepSleep(1800e6); // 1e6 is 1 second
          }

      else

          {
            Serial.println("No WiFi");
            delay(5000);
          }
                       
    }
