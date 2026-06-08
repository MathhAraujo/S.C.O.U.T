#include <Arduino.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <Wire.h>
#include <Protocentral_MAX30205.h>

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#warning "Using secrets.example.h. Copy it to secrets.h and configure real credentials before flashing hardware."
#endif

#define SENSOR_READ_INTERVAL_MS 1000
#define TEMPERATURE_OFFSET_CELSIUS 0.0f

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
MAX30205 temperatureSensor;

unsigned long lastSensorReadAt = 0;

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  Serial.print("Connecting to Wi-Fi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Wi-Fi connected: ");
  Serial.println(WiFi.localIP());
}

void connectMqtt() {
  if (mqttClient.connected()) {
    return;
  }

  while (!mqttClient.connected()) {
    connectWiFi();

    String clientId = String(DEVICE_ID) + "-client";
    Serial.print("Connecting to MQTT broker ");
    Serial.print(MQTT_HOST);
    Serial.print(":");
    Serial.println(MQTT_PORT);

    if (mqttClient.connect(clientId.c_str())) {
      Serial.println("MQTT connected");
      return;
    }

    Serial.print("MQTT connection failed, rc=");
    Serial.println(mqttClient.state());
    delay(2000);
  }
}

void publishTemperature() {
  float rawTemperature = temperatureSensor.getTemperature();
  if (isnan(rawTemperature)) {
    Serial.println("MAX30205 returned an invalid temperature");
    return;
  }

  float adjustedTemperature = rawTemperature + TEMPERATURE_OFFSET_CELSIUS;

  JsonDocument payload;
  payload["device_id"] = DEVICE_ID;
  payload["sensor"] = "MAX30205";
  payload["value_celsius"] = adjustedTemperature;
  payload["unit"] = "celsius";
  payload["firmware_version"] = FIRMWARE_VERSION;
  payload["uptime_ms"] = millis();

  char topic[128];
  snprintf(topic, sizeof(topic), "athletes/%s/temperature", DEVICE_ID);

  char buffer[256];
  size_t length = serializeJson(payload, buffer, sizeof(buffer));
  bool published = mqttClient.publish(topic, buffer, length);

  if (published) {
    Serial.print("Published temperature to ");
    Serial.println(topic);
  } else {
    Serial.println("Failed to publish temperature");
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Wire.begin();
  temperatureSensor.begin();

  bool sensorFound = temperatureSensor.scanAvailableSensors();
  if (!sensorFound) {
    Serial.println("MAX30205 not found on I2C bus");
  }

  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  connectWiFi();
  connectMqtt();
}

void loop() {
  connectWiFi();
  connectMqtt();
  mqttClient.loop();

  unsigned long now = millis();
  if (now - lastSensorReadAt >= SENSOR_READ_INTERVAL_MS) {
    lastSensorReadAt = now;
    publishTemperature();
  }
}
