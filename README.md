# S.C.O.U.T

Sistema local para receber leituras de temperatura de uma ESP32 com sensor NTC via MQTT, encaminhar pelo Node-RED e persistir no backend FastAPI com PostgreSQL.

## Requisitos

- Docker e Docker Compose
- PlatformIO, apenas para compilar e gravar o firmware na ESP32

## Configurar ambiente

No PowerShell:

```powershell
Copy-Item .env.example .env
```

Em bash:

```bash
cp .env.example .env
```

## Criar banco e rodar migrações

```bash
docker compose up --build -d postgres
docker compose run --rm backend alembic upgrade head
```

## Subir o sistema

```bash
docker compose up --build
```

## Acessos locais

```text
Backend: http://localhost:8000
Health check: http://localhost:8000/health
Node-RED: http://localhost:1880
Frontend: http://localhost:5173
PostgreSQL: localhost:5432
MQTT: localhost:1883
```

## Firmware

Crie o arquivo de configuração da ESP32:

```bash
cp firmware/include/secrets.example.h firmware/include/secrets.h
```

Edite `firmware/include/secrets.h` com:

```cpp
#define WIFI_SSID "your-wifi-ssid"
#define WIFI_PASSWORD "your-wifi-password"
#define MQTT_HOST "192.168.0.100"
#define MQTT_PORT 1883
#define DEVICE_ID "esp32-prototype-001"
#define FIRMWARE_VERSION "0.1.0"
```

`MQTT_HOST` deve ser o IP da máquina que está rodando o Docker Compose.

Compile e envie para a placa:

```bash
cd firmware
pio run --target upload
```
