#include <Arduino.h>
#include <ArduinoJson.h>
#include <math.h>
#include <PubSubClient.h>
#include <WiFi.h>

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#warning "Using secrets.example.h. Copy it to secrets.h and configure real credentials before flashing hardware."
#endif

#define SENSOR_READ_INTERVAL_MS 1000
#define TEMPERATURE_OFFSET_CELSIUS 0.0f
#define NTC_ADC_PIN 34
#define NTC_ADC_MAX_VALUE 4095.0f
#define NTC_ADC_SAMPLES 16
#define NTC_ADC_SAMPLE_DELAY_MS 2
#define NTC_SERIES_RESISTOR_OHMS 10000.0f
#define NTC_NOMINAL_RESISTANCE_OHMS 10000.0f
#define NTC_NOMINAL_TEMPERATURE_CELSIUS 25.0f
#define NTC_BETA_COEFFICIENT 3950.0f
#define NTC_CONNECTED_TO_GROUND 1
#define WIFI_CONNECT_MAX_ATTEMPTS 60
#define MQTT_CONNECT_MAX_ATTEMPTS 5
#define MIN_VALID_TEMPERATURE_CELSIUS 15.0f
#define MAX_VALID_TEMPERATURE_CELSIUS 45.0f

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

unsigned long lastSensorReadAt = 0;

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

float readAverageAdcValue() {
  uint32_t adcSum = 0;

  for (uint8_t sample = 0; sample < NTC_ADC_SAMPLES; sample++) {
    adcSum += analogRead(NTC_ADC_PIN);
    delay(NTC_ADC_SAMPLE_DELAY_MS);
  }

  return static_cast<float>(adcSum) / static_cast<float>(NTC_ADC_SAMPLES);
}

float calculateNtcResistance(float adcValue) {
  if (adcValue <= 0.0f || adcValue >= NTC_ADC_MAX_VALUE) {
    return NAN;
  }

#if NTC_CONNECTED_TO_GROUND
  return NTC_SERIES_RESISTOR_OHMS * adcValue / (NTC_ADC_MAX_VALUE - adcValue);
#else
  return NTC_SERIES_RESISTOR_OHMS * (NTC_ADC_MAX_VALUE - adcValue) / adcValue;
#endif
}

float calculateTemperatureCelsius(float resistanceOhms) {
  if (isnan(resistanceOhms) || resistanceOhms <= 0.0f) {
    return NAN;
  }

  const float nominalTemperatureKelvin = NTC_NOMINAL_TEMPERATURE_CELSIUS + 273.15f;
  const float inverseTemperatureKelvin =
      (logf(resistanceOhms / NTC_NOMINAL_RESISTANCE_OHMS) / NTC_BETA_COEFFICIENT) +
      (1.0f / nominalTemperatureKelvin);

  return (1.0f / inverseTemperatureKelvin) - 273.15f;
}

float readNtcTemperature() {
  float adcValue = readAverageAdcValue();
  float resistanceOhms = calculateNtcResistance(adcValue);

  return calculateTemperatureCelsius(resistanceOhms);
}

void publishTemperature() {
  float rawTemperature = readNtcTemperature();
  float adjustedTemperature = rawTemperature + TEMPERATURE_OFFSET_CELSIUS;

  if (isnan(adjustedTemperature) ||
      adjustedTemperature < MIN_VALID_TEMPERATURE_CELSIUS ||
      adjustedTemperature > MAX_VALID_TEMPERATURE_CELSIUS) {
    Serial.println("NTC returned an invalid temperature, skipping publish");
    return;
  }

  JsonDocument payload;
  payload["device_uid"] = DEVICE_ID;
  payload["sensor"] = "NTC";
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

  analogReadResolution(12);
  analogSetPinAttenuation(NTC_ADC_PIN, ADC_11db);
  pinMode(NTC_ADC_PIN, INPUT);
  Serial.print("NTC sensor configured on GPIO");
  Serial.println(NTC_ADC_PIN);

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
    publishTemperature();
  }
}
