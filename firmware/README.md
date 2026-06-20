# Firmware

Firmware PlatformIO para ESP32 usando Arduino Framework, Wi-Fi, MQTT, I2C e MAX30205.

## Configuracao

Copie `include/secrets.example.h` para `include/secrets.h` e ajuste:

- `WIFI_SSID`
- `WIFI_PASSWORD`
- `MQTT_HOST`
- `MQTT_PORT`
- `DEVICE_ID`
- `FIRMWARE_VERSION`

O arquivo `include/secrets.h` nao e versionado.

## Sensor

O MAX30205 deve ser ligado via I2C. A leitura inicial ocorre a cada 1 segundo, controlada por `SENSOR_READ_INTERVAL_MS`. O offset opcional `TEMPERATURE_OFFSET_CELSIUS` tem valor padrao zero.

As leituras dependem do contato com a pele, da fixacao fisica, da posicao de uso, de roupa, suor e ambiente. O prototipo registra dados, mas nao gera diagnostico medico.
