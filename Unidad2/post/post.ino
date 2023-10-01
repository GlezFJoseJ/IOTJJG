#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

#define DHTPIN 18
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

const char *ssid = "W_Aula_WB11";
const char *password = "itcolima6";

String serverName = "http://e672-187-190-35-202.ngrok-free.app";

unsigned long lastTime = 0;
unsigned long timerDelay = 3000;

// Define los pines para los botones
const int buttonPinAsc = 2; // Cambia al número de pin que estás utilizando
const int buttonPinDesc = 4; // Cambia al número de pin que estás utilizando

const int ledPin = 5;

bool ascRequested = false; // Bandera para controlar la solicitud "asc"
bool descRequested = false; // Bandera para controlar la solicitud "desc"

void setup() {
  Serial.begin(115200);
  dht.begin();
  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());

  // Configura los pines de los botones como entradas
  pinMode(buttonPinAsc, INPUT_PULLUP);
  pinMode(buttonPinDesc, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);

  Serial.println("Timer set to 5 seconds (timerDelay variable), it will take 5 seconds before publishing the first reading.");
}

void loop() {
  // Temperatura
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature)) {
    Serial.println("Error al leer el sensor DHT!");
    return;
  }

  Serial.println(temperature);
  Serial.println(humidity);

  // Verifica si el botón "asc" se ha presionado
  if (digitalRead(buttonPinAsc) == HIGH && !ascRequested) {
    ascRequested = true;
  }

  // Verifica si el botón "desc" se ha presionado
  if (digitalRead(buttonPinDesc) == HIGH && !descRequested) {
    descRequested = true;
  }

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Envio del POST de la temperatura
    String serverPath = serverName + "/temperature";

    http.begin(serverPath.c_str());

    DynamicJsonDocument jsonDocTemp(64);

    jsonDocTemp["temperature"] = temperature; // Cambia la cantidad según tu necesidad

    String jsonString;
    serializeJson(jsonDocTemp, jsonString);

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

    serverPath = serverName + "/humidity";

    http.begin(serverPath.c_str());

    DynamicJsonDocument jsonDocHum(64);

    jsonDocHum["humidity"] = humidity; // Cambia la cantidad según tu necesidad

    String jsonStringHum;
    serializeJson(jsonDocHum, jsonStringHum);

    http.addHeader("Content-Type", "application/json");

    httpResponseCode = http.POST(jsonStringHum);

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

    // Get del status del led
    String serverPathLed = serverName + "/led";

    http.begin(serverPathLed.c_str());

    // Send HTTP GET request
    int httpResponseCodeGET = http.GET();
    
    if (httpResponseCodeGET>0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCodeGET);
      String payload = http.getString();
      Serial.println(payload);

      DynamicJsonDocument doc(1024);
      deserializeJson(doc, payload);

      int led = doc["led"];
      Serial.println(led);

      if (led == 0) {
        digitalWrite(ledPin, LOW);
      }
      if (led == 1) {
        digitalWrite(ledPin, HIGH);
      }
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCodeGET);
    }

    http.end();

    if (ascRequested || descRequested) {
      if ((millis() - lastTime) > timerDelay) {
          serverPath = serverName + "/led";

          http.begin(serverPath.c_str());

          DynamicJsonDocument jsonDoc(64);

          if (ascRequested) {
            jsonDoc["action"] = "asc";
            ascRequested = false; // Restablece la bandera después de la solicitud
          } else if (descRequested) {
            jsonDoc["action"] = "desc";
            descRequested = false; // Restablece la bandera después de la solicitud
          }
          jsonDoc["quantity"] = 1; // Cambia la cantidad según tu necesidad

          String jsonStringCounter;
          serializeJson(jsonDoc, jsonStringCounter);

          http.addHeader("Content-Type", "application/json");

          httpResponseCode = http.POST(jsonStringCounter);

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
        lastTime = millis();
      }
    }
  } else {
    Serial.println("WiFi Disconnected");
  }
  delay(500);
}