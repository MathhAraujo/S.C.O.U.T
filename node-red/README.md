# Node-RED

Node-RED roda o broker MQTT Aedes na porta `1883`, escuta o topico `athletes/+/temperature`, valida minimamente o payload e encaminha mensagens validas para:

```text
http://backend:8000/api/v1/telemetry/temperature
```

O Node-RED nao persiste dados e nao aplica regra de negocio de atleta ou dispositivo.
