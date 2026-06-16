# Firmware

Firmware PlatformIO para ESP32 usando Arduino Framework, Wi-Fi, MQTT e sensor de temperatura NTC.

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

O NTC deve ser ligado em um divisor de tensao no GPIO34 por padrao. A configuracao esperada e:

```text
3V3 -> resistor 10k -> GPIO34 -> NTC 10k -> GND
```

A leitura ocorre a cada 1 segundo, controlada por `SENSOR_READ_INTERVAL_MS`. O offset opcional `TEMPERATURE_OFFSET_CELSIUS` tem valor padrao zero.

Os parametros do divisor e da curva Beta ficam em `src/main.cpp`:

- `NTC_ADC_PIN`
- `NTC_SERIES_RESISTOR_OHMS`
- `NTC_NOMINAL_RESISTANCE_OHMS`
- `NTC_NOMINAL_TEMPERATURE_CELSIUS`
- `NTC_BETA_COEFFICIENT`
- `NTC_CONNECTED_TO_GROUND`

As leituras dependem do contato com a pele, da fixacao fisica, da posicao de uso, de roupa, suor e ambiente. O prototipo registra dados, mas nao gera diagnostico medico.
