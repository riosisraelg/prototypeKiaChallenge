# KIA Paint Shop IoT Simulator

Simulador de datos IoT para el prototipo de digitalización del Paint Shop de KIA.

## Descripción

Este simulador genera datos realistas para ~100 variables del proceso de pintura y los publica a AWS IoT Core mediante MQTT. Incluye:

- **Generación de datos**: Valores aleatorios dentro de rangos configurados
- **Detección de alarmas**: Identifica cuando los valores exceden umbrales
- **Publicación MQTT**: Envía datos a AWS IoT Core con autenticación X.509
- **Manejo de errores**: Reconexión automática con backoff exponencial

## Requisitos

- Python 3.11+
- Dependencias instaladas: `pip install -r ../requirements.txt`
- Certificados X.509 de AWS IoT Core en `certs/`
- Endpoint de AWS IoT Core configurado en `config.yaml`

## Estructura de Archivos

```
simulator/
├── simulator.py           # Script principal
├── config_loader.py       # Carga variables desde CSV
├── data_generator.py      # Genera datos aleatorios
├── mqtt_publisher.py      # Publica a AWS IoT Core
├── alarm_simulator.py     # Detecta alarmas
├── config.yaml           # Configuración
├── data/                 # Archivos CSV con variables
│   ├── KMX-PA-PT-F-001.csv
│   ├── KMX-PA-PE-F-001.csv
│   └── production_control.csv
└── certs/                # Certificados X.509 (no incluidos)
    ├── device.crt
    ├── device.key
    └── AmazonRootCA1.pem
```

## Configuración

### 1. Configurar endpoint de IoT Core

Editar `config.yaml` y establecer el endpoint:

```yaml
mqtt:
  endpoint: "xxxxx-ats.iot.us-east-1.amazonaws.com"
  port: 8883
  cert_path: "certs/device.crt"
  key_path: "certs/device.key"
  ca_path: "certs/AmazonRootCA1.pem"
```

### 2. Obtener certificados

Los certificados se generan con Terraform o manualmente desde AWS IoT Core:

```bash
# Descargar certificado raíz de Amazon
curl -o certs/AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem

# Copiar certificados generados por Terraform
cp ../terraform/outputs/device.crt certs/
cp ../terraform/outputs/device.key certs/
```

### 3. Ajustar parámetros de simulación

En `config.yaml`:

```yaml
simulation:
  interval_seconds: 30        # Intervalo entre ciclos
  anomaly_probability: 0.05   # 5% probabilidad de anomalía
  max_variables: 100          # Máximo de variables a simular
  enable_alarms: true         # Habilitar detección de alarmas
```

## Uso

### Ejecutar el simulador

```bash
cd simulator
python simulator.py
```

O especificar un archivo de configuración diferente:

```bash
python simulator.py /path/to/config.yaml
```

### Detener el simulador

Presionar `Ctrl+C` para detener limpiamente. El simulador:
- Cierra la conexión MQTT
- Imprime estadísticas finales
- Sale sin errores

### Salida esperada

```
============================================================
KIA Paint Shop IoT Simulator
============================================================
Variables: 97
Interval: 30 seconds
Anomaly probability: 0.05
MQTT endpoint: xxxxx-ats.iot.us-east-1.amazonaws.com
============================================================

Press Ctrl+C to stop

2024-01-15 10:30:00 - Starting cycle 1
2024-01-15 10:30:01 - Cycle 1 complete: 97 published, 0 failed

============================================================
Progress Report - Cycle 10
============================================================
Uptime: 5m 0s
Messages sent: 970
Messages failed: 0
Alarms generated: 12
  - Warnings: 8
  - Critical: 4
============================================================
```

## Estructura de Mensajes MQTT

### Topic

```
kia/paintshop/{area}/{variable_id}
```

Ejemplos:
- `kia/paintshop/pre-treatment/PT-001`
- `kia/paintshop/e-coat/ED-005`
- `kia/paintshop/production-control/PC-020`

### Payload

```json
{
  "variable_id": "PT-001",
  "area": "pre-treatment",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "value": 65.5,
  "unit": "°C",
  "quality": "good",
  "metadata": {
    "min_range": 60.0,
    "max_range": 70.0,
    "alarm_low": 62.0,
    "alarm_high": 68.0
  },
  "alarm": {
    "is_alarm": false
  }
}
```

Con alarma:

```json
{
  "variable_id": "PT-001",
  "area": "pre-treatment",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "value": 71.2,
  "unit": "°C",
  "quality": "uncertain",
  "metadata": {
    "min_range": 60.0,
    "max_range": 70.0,
    "alarm_low": 62.0,
    "alarm_high": 68.0
  },
  "alarm": {
    "is_alarm": true,
    "severity": "critical",
    "threshold_type": "high",
    "threshold_value": 68.0,
    "exceedance_percent": 16.0,
    "message": "Temperature above high threshold: 71.20 > 68.00 °C"
  }
}
```

## Pruebas

### Prueba local completa (sin AWS)

Para verificar que todos los componentes funcionan sin necesidad de AWS:

```bash
cd simulator
python test_simulator_local.py
```

Este script prueba:
- ✅ Carga de configuración (97 variables)
- ✅ Generación de datos aleatorios
- ✅ Detección de alarmas
- ✅ Formato de mensajes

### Probar componentes individuales

```bash
# Probar carga de configuración
python config_loader.py

# Probar generación de datos
python data_generator.py

# Probar detección de alarmas
python alarm_simulator.py

# Probar publicación MQTT (requiere configuración)
python mqtt_publisher.py
```

### Verificar conectividad con IoT Core

```bash
# Verificar que los certificados son válidos
openssl x509 -in certs/device.crt -text -noout

# Probar conexión MQTT (requiere mosquitto-clients)
mosquitto_pub \
  --cafile certs/AmazonRootCA1.pem \
  --cert certs/device.crt \
  --key certs/device.key \
  -h xxxxx-ats.iot.us-east-1.amazonaws.com \
  -p 8883 \
  -t "kia/paintshop/test" \
  -m '{"test": true}'
```

## Troubleshooting

### Error: "MQTT endpoint not configured"

**Solución**: Editar `config.yaml` y establecer `mqtt.endpoint`

### Error: "Certificate not found"

**Solución**: Verificar que los certificados están en `certs/` y los paths en `config.yaml` son correctos

### Error: "Connection refused"

**Causas posibles**:
- Endpoint incorrecto
- Certificados inválidos o expirados
- Policy de IoT Core no permite publish en los topics
- Firewall bloqueando puerto 8883

**Solución**: Verificar configuración en AWS IoT Core Console

### Error: "Connection timeout"

**Causas posibles**:
- Problemas de red
- Endpoint incorrecto
- Puerto 8883 bloqueado

**Solución**: Verificar conectividad de red y firewall

### Mensajes no llegan a IoT Core

**Verificar**:
1. Conexión MQTT establecida (logs del simulador)
2. IoT Rule configurada correctamente
3. CloudWatch Logs de IoT Core para errores
4. Policy permite publish en `kia/paintshop/*`

## Logging

### Configurar nivel de log

En `config.yaml`:

```yaml
logging:
  level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
  format: "json"  # json o text
  file: "simulator.log"  # Opcional
```

### Ver logs en tiempo real

```bash
tail -f simulator.log
```

### Formato JSON

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "logger": "simulator",
  "message": "Cycle 1 complete: 97 published, 0 failed"
}
```

## Métricas

El simulador registra las siguientes métricas:

- **Cycles completed**: Número de ciclos completados
- **Messages sent**: Total de mensajes publicados exitosamente
- **Messages failed**: Total de mensajes que fallaron
- **Alarms generated**: Total de alarmas detectadas
  - Warnings: Alarmas de severidad warning
  - Critical: Alarmas de severidad critical
- **Connection attempts**: Intentos de conexión a IoT Core
- **Uptime**: Tiempo total de ejecución

## Variables Simuladas

### Pre-Treatment (45 variables)

Variables del proceso de pre-tratamiento desde `KMX-PA-PT-F-001.csv`:
- Temperaturas de tanques
- Niveles de pH
- Conductividad
- Flujos de agua
- Presiones

### E-Coat (18 variables)

Variables del proceso de electrodeposición desde `KMX-PA-PE-F-001.csv`:
- Voltaje
- Corriente
- Temperatura de baño
- pH
- Conductividad

### Production Control (34 variables)

Variables de control de producción (sintéticas):
- Velocidad de línea
- Throughput
- Calidad de pintura
- Consumo de energía
- Métricas de eficiencia (OEE, FPY)

## Desarrollo

### Agregar nuevas variables

1. Editar archivos CSV en `data/` o agregar en `config_loader.py`
2. Reiniciar el simulador

### Modificar lógica de alarmas

Editar `alarm_simulator.py` y ajustar:
- Umbrales de severidad
- Cálculo de exceedance
- Mensajes de alarma

### Cambiar generación de datos

Editar `data_generator.py` y ajustar:
- Probabilidad de anomalías
- Suavizado de transiciones
- Precisión de valores

## Licencia

Prototipo interno para demostración - KIA Paint Shop IoT
