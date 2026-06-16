#include <Arduino.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFi.h>

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#warning "Using secrets.example.h. Copy it to secrets.h and configure real credentials before flashing hardware."
#endif

#define SENSOR_READ_INTERVAL_MS 1000
#define NTC_DIGITAL_PIN 34
#define NTC_THRESHOLD_CELSIUS 30.0f
#define NTC_ABOVE_THRESHOLD_LEVEL LOW
#define WIFI_CONNECT_MAX_ATTEMPTS 60
#define MQTT_CONNECT_MAX_ATTEMPTS 5

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

unsigned long lastSensorReadAt = 0;

struct NtcThresholdReading {
  int digitalLevel;
  bool aboveThreshold;
};

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

const char *digitalLevelName(int digitalLevel) {
  return digitalLevel == HIGH ? "HIGH" : "LOW";
}

NtcThresholdReading readNtcThreshold() {
  int digitalLevel = digitalRead(NTC_DIGITAL_PIN);

  return {
      digitalLevel,
      digitalLevel == NTC_ABOVE_THRESHOLD_LEVEL};
}

void publishTemperatureStatus() {
  NtcThresholdReading reading = readNtcThreshold();

  Serial.print("NTC threshold: ");
  Serial.print(NTC_THRESHOLD_CELSIUS, 2);
  Serial.print(" C | DO: ");
  Serial.print(digitalLevelName(reading.digitalLevel));
  Serial.print(" | status: ");
  Serial.println(reading.aboveThreshold ? "above threshold" : "below threshold");

  JsonDocument payload;
  payload["device_uid"] = DEVICE_ID;
  payload["sensor"] = "NTC_LM393";
  payload["threshold_celsius"] = NTC_THRESHOLD_CELSIUS;
  payload["above_threshold"] = reading.aboveThreshold;
  payload["digital_level"] = digitalLevelName(reading.digitalLevel);
  payload["firmware_version"] = FIRMWARE_VERSION;
  payload["uptime_ms"] = millis();

  char topic[128];
  snprintf(topic, sizeof(topic), "athletes/%s/temperature-threshold", DEVICE_ID);

  char buffer[256];
  size_t length = serializeJson(payload, buffer, sizeof(buffer));
  bool published = mqttClient.publish(
      topic,
      reinterpret_cast<const uint8_t *>(buffer),
      static_cast<unsigned int>(length),
      false);

  if (published) {
    Serial.print("Published threshold status to ");
    Serial.println(topic);
  } else {
    Serial.println("Failed to publish threshold status");
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(NTC_DIGITAL_PIN, INPUT);
  Serial.print("NTC LM393 digital output configured on GPIO");
  Serial.println(NTC_DIGITAL_PIN);
  Serial.print("NTC threshold point configured as ");
  Serial.print(NTC_THRESHOLD_CELSIUS, 2);
  Serial.println(" C");

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
    publishTemperatureStatus();
  }
}
