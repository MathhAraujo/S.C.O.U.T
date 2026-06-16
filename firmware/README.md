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

## Sensor LM393

O modulo NTC com LM393 deve ser ligado pela saida digital `DO` no GPIO34 por padrao:

```text
VCC -> 3V3
GND -> GND
DO  -> GPIO34
```

A leitura ocorre a cada 1 segundo, controlada por `SENSOR_READ_INTERVAL_MS`.

O ponto de limite usado pelo firmware e `NTC_THRESHOLD_CELSIUS`, definido como 30 C. Como o modulo usa o comparador LM393, esse ponto precisa ser calibrado fisicamente no trimpot do modulo. O firmware le apenas se a saida `DO` esta acima ou abaixo desse limite; ele nao mede a temperatura exata em Celsius.

Os parametros do modulo ficam em `src/main.cpp`:

- `NTC_DIGITAL_PIN`
- `NTC_THRESHOLD_CELSIUS`
- `NTC_ABOVE_THRESHOLD_LEVEL`

Se o status aparecer invertido no monitor serial, troque `NTC_ABOVE_THRESHOLD_LEVEL` de `LOW` para `HIGH` em `src/main.cpp`.

As leituras dependem do contato com a pele, da fixacao fisica, da posicao de uso, de roupa, suor e ambiente. O prototipo registra dados, mas nao gera diagnostico medico.
