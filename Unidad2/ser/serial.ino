#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char *ssid = "W_Aula_WB11";
const char *password = "itcolima6";

String serverName = "http://192.168.4.8:7800/";

unsigned long lastTime = 0;
unsigned long timerDelay = 5000;

void setup() 
{
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop()
{
  if(Serial.available()) 
  {
    String data = Serial.readStringUntil('\n');
    if ((millis() - lastTime) > timerDelay) {
      if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;

        String serverPath = serverName;

        http.begin(serverPath.c_str());

        DynamicJsonDocument jsonDoc(64);

        if (data == "+") {
          Serial.println("Post to asc");
          jsonDoc["action"] = "asc";
        }
        else if (data == "-") {
          Serial.println("Post to desc");
          jsonDoc["action"] = "desc";
        }
        else {
          Serial.println("Invalid command");
        }

        jsonDoc["quantity"] = 1; // Cambia la cantidad según tu necesidad

        String jsonString;
        serializeJson(jsonDoc, jsonString);

        http.addHeader("Content-Type", "application/json");

        int httpResponseCode = http.POST(jsonString);

        if (httpResponseCode > 0) {
          Serial.print("HTTP Response code: ");
          Serial.println(httpResponseCode);
          String payload = http.getString();
          Serial.println(payload);
        } else {
          Serial.print("Error code: ");
          Serial.println(httpResponseCode);
        }
        http.end();
      } else {
        Serial.println("WiFi Disconnected");
      }
      lastTime = millis();
    }
  }
}