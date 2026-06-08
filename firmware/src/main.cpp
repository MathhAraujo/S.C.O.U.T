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
#define WIFI_CONNECT_MAX_ATTEMPTS 60
#define MQTT_CONNECT_MAX_ATTEMPTS 5
#define MIN_VALID_TEMPERATURE_CELSIUS 15.0f
#define MAX_VALID_TEMPERATURE_CELSIUS 45.0f

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
MAX30205 temperatureSensor;

unsigned long lastSensorReadAt = 0;
bool sensorAvailable = false;

bool connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    return true;
  }

  Serial.print("Connecting to Wi-Fi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  for (int attempt = 0; attempt < WIFI_CONNECT_MAX_ATTEMPTS && WiFi.status() != WL_CONNECTED; attempt++) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println();
    Serial.println("Wi-Fi connection failed");
    return false;
  }

  Serial.println();
  Serial.print("Wi-Fi connected: ");
  Serial.println(WiFi.localIP());
  return true;
}

bool connectMqtt() {
  if (mqttClient.connected()) {
    return true;
  }

  static char clientId[64];
  snprintf(clientId, sizeof(clientId), "%s-client", DEVICE_ID);

  for (int attempt = 0; attempt < MQTT_CONNECT_MAX_ATTEMPTS; attempt++) {
    if (!connectWiFi()) {
      return false;
    }

    Serial.print("Connecting to MQTT broker ");
    Serial.print(MQTT_HOST);
    Serial.print(":");
    Serial.println(MQTT_PORT);

    if (mqttClient.connect(clientId)) {
      Serial.println("MQTT connected");
      return true;
    }

    Serial.print("MQTT connection failed, rc=");
    Serial.println(mqttClient.state());
    delay(2000);
  }

  Serial.println("MQTT connection failed after maximum attempts");
  return false;
}

void publishTemperature() {
  float rawTemperature = temperatureSensor.getTemperature();
  float adjustedTemperature = rawTemperature + TEMPERATURE_OFFSET_CELSIUS;

  if (isnan(adjustedTemperature) ||
      adjustedTemperature < MIN_VALID_TEMPERATURE_CELSIUS ||
      adjustedTemperature > MAX_VALID_TEMPERATURE_CELSIUS) {
    Serial.println("MAX30205 returned an invalid temperature, skipping publish");
    return;
  }

  JsonDocument payload;
  payload["device_uid"] = DEVICE_ID;
  payload["sensor"] = "MAX30205";
  payload["value_celsius"] = adjustedTemperature;
  payload["unit"] = "celsius";
  payload["firmware_version"] = FIRMWARE_VERSION;
  payload["uptime_ms"] = millis();

  char topic[128];
  snprintf(topic, sizeof(topic), "athletes/%s/temperature", DEVICE_ID);

  char buffer[256];
  size_t length = serializeJson(payload, buffer, sizeof(buffer));
  bool published = mqttClient.publish(
      topic,
      reinterpret_cast<const uint8_t *>(buffer),
      static_cast<unsigned int>(length),
      false);

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

  sensorAvailable = temperatureSensor.scanAvailableSensors();
  if (!sensorAvailable) {
    Serial.println("MAX30205 not found on I2C bus");
  }

  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  connectWiFi();
  connectMqtt();
}

void loop() {
  if (!connectWiFi()) {
    return;
  }

  if (!connectMqtt()) {
    return;
  }

  mqttClient.loop();

  unsigned long now = millis();
  if (now - lastSensorReadAt >= SENSOR_READ_INTERVAL_MS) {
    lastSensorReadAt = now;
    if (!sensorAvailable) {
      Serial.println("Temperature sensor unavailable, skipping publish");
      return;
    }

    publishTemperature();
  }
}
