# Checkpoint 5: Verificación del Simulador

## Estado Actual

✅ **Simulador implementado completamente**
- Script principal: `simulator.py`
- Componentes: ConfigLoader, DataGenerator, MQTTPublisher, AlarmSimulator
- Configuración: `config.yaml`
- Property tests: 5 propiedades validadas

## Pasos de Verificación

### 1. Verificar que Terraform está desplegado

Primero, asegúrate de que la infraestructura de AWS IoT Core está desplegada:

```bash
cd terraform
terraform output iot_endpoint
```

**Resultado esperado**: Debe mostrar un endpoint como `xxxxx-ats.iot.us-east-1.amazonaws.com`

Si no hay output o muestra error, necesitas desplegar la infraestructura:

```bash
terraform init
terraform plan
terraform apply
```

### 2. Descargar certificados de IoT Core

Los certificados se generan automáticamente con Terraform. Necesitas copiarlos al directorio del simulador:

```bash
# Desde la raíz del proyecto
cd terraform

# Verificar que los certificados fueron creados
ls -la *.pem *.crt *.key 2>/dev/null

# Copiar certificados al directorio del simulador
cp device.crt ../simulator/certs/
cp device.key ../simulator/certs/
chmod 600 ../simulator/certs/device.key

# Descargar el certificado raíz de Amazon
cd ../simulator/certs
curl -o AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem
```

**Verificar que los certificados están en su lugar:**

```bash
ls -la simulator/certs/
```

Debes ver:
- `device.crt` - Certificado del dispositivo
- `device.key` - Clave privada (permisos 600)
- `AmazonRootCA1.pem` - Certificado raíz de Amazon

### 3. Configurar el endpoint en config.yaml

Edita `simulator/config.yaml` y establece el endpoint de IoT Core:

```bash
# Obtener el endpoint
cd terraform
ENDPOINT=$(terraform output -raw iot_endpoint)
echo "Endpoint: $ENDPOINT"

# Actualizar config.yaml
cd ../simulator
# Editar manualmente o usar sed:
sed -i.bak "s|endpoint: \"\"|endpoint: \"$ENDPOINT\"|" config.yaml
```

**Verificar la configuración:**

```bash
cat simulator/config.yaml | grep endpoint
```

Debe mostrar algo como:
```yaml
endpoint: "xxxxx-ats.iot.iot.us-east-1.amazonaws.com"
```

### 4. Instalar dependencias de Python

```bash
# Desde la raíz del proyecto
pip install -r requirements.txt
```

### 5. Ejecutar el simulador localmente

```bash
cd simulator
python simulator.py
```

**Salida esperada:**

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

2024-01-15 10:30:00 - simulator - INFO - Starting cycle 1
2024-01-15 10:30:01 - simulator - INFO - Cycle 1 complete: 97 published, 0 failed
```

**Indicadores de éxito:**
- ✅ Conexión MQTT establecida
- ✅ Mensajes publicados exitosamente (97 published, 0 failed)
- ✅ No hay errores de conexión o certificados

**Indicadores de problemas:**
- ❌ "MQTT endpoint not configured" → Falta configurar endpoint en config.yaml
- ❌ "Certificate not found" → Faltan certificados en certs/
- ❌ "Connection refused" → Endpoint incorrecto o certificados inválidos
- ❌ "Connection timeout" → Problemas de red o firewall

### 6. Verificar mensajes en AWS IoT Core

Mientras el simulador está corriendo, verifica que los mensajes llegan a IoT Core:

**Opción A: AWS IoT Test Client (Console)**

1. Ir a AWS Console → IoT Core → Test
2. Suscribirse al topic: `kia/paintshop/#`
3. Deberías ver mensajes llegando cada 30 segundos

**Opción B: AWS CLI**

```bash
# Suscribirse a los topics (requiere AWS CLI v2)
aws iot-data subscribe \
  --topic 'kia/paintshop/#' \
  --region us-east-1
```

**Opción C: CloudWatch Logs**

```bash
# Ver logs de la IoT Rule
aws logs tail /aws/iot/rules/kia-paintshop-prototype --follow
```

### 7. Verificar estructura de topics y payload

Los mensajes deben seguir esta estructura:

**Topic:**
```
kia/paintshop/{area}/{variable_id}
```

Ejemplos:
- `kia/paintshop/pre-treatment/PT-001`
- `kia/paintshop/e-coat/ED-005`
- `kia/paintshop/production-control/PC-020`

**Payload:**
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

### 8. Verificar generación de alarmas

Deja el simulador corriendo por algunos minutos. Deberías ver alarmas generadas ocasionalmente:

```
2024-01-15 10:32:00 - simulator - INFO - Cycle 5: 3 alarms detected
```

Verifica que los mensajes con alarmas tienen el campo `alarm.is_alarm: true`:

```json
{
  "variable_id": "PT-001",
  "value": 71.2,
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

### 9. Detener el simulador

Presiona `Ctrl+C` para detener el simulador limpiamente.

**Salida esperada:**

```
^C
Received SIGINT, shutting down gracefully...

============================================================
Final Statistics
============================================================
Total uptime: 5m 0s
Cycles completed: 10
Messages sent: 970
Messages failed: 0
Connection attempts: 1
Alarms generated: 12
  - Warnings: 8
  - Critical: 4
============================================================
```

## Checklist de Verificación

Marca cada item cuando lo hayas verificado:

- [ ] Terraform desplegado correctamente
- [ ] Endpoint de IoT Core obtenido
- [ ] Certificados copiados a `simulator/certs/`
- [ ] Certificado raíz de Amazon descargado
- [ ] `config.yaml` actualizado con endpoint correcto
- [ ] Dependencias de Python instaladas
- [ ] Simulador inicia sin errores
- [ ] Conexión MQTT establecida exitosamente
- [ ] Mensajes publicados (0 failed)
- [ ] Mensajes visibles en AWS IoT Test Client
- [ ] Estructura de topics correcta (`kia/paintshop/{area}/{variable_id}`)
- [ ] Formato de payload correcto (JSON válido)
- [ ] Alarmas generadas ocasionalmente
- [ ] Simulador se detiene limpiamente con Ctrl+C
- [ ] Estadísticas finales mostradas

## Problemas Comunes y Soluciones

### Problema: "ModuleNotFoundError: No module named 'yaml'"

**Solución:**
```bash
pip install pyyaml
```

### Problema: "ModuleNotFoundError: No module named 'paho'"

**Solución:**
```bash
pip install paho-mqtt
```

### Problema: Certificados no encontrados en terraform/

**Causa**: Los certificados se generan con Terraform pero pueden estar en un subdirectorio.

**Solución:**
```bash
cd terraform
# Buscar certificados
find . -name "*.crt" -o -name "*.key"

# Si están en un subdirectorio, copiarlos
cp path/to/device.crt ../simulator/certs/
cp path/to/device.key ../simulator/certs/
```

### Problema: "Connection refused" o "Connection timeout"

**Causas posibles:**
1. Endpoint incorrecto en config.yaml
2. Certificados inválidos o expirados
3. Policy de IoT Core no permite publish
4. Firewall bloqueando puerto 8883

**Solución:**
```bash
# Verificar endpoint
cd terraform
terraform output iot_endpoint

# Verificar certificado
openssl x509 -in ../simulator/certs/device.crt -text -noout | grep "Not After"

# Verificar policy en AWS Console
# IoT Core → Secure → Policies → kia-paintshop-prototype-policy
```

### Problema: Mensajes no llegan a IoT Core

**Verificar:**
1. Simulador muestra "published" exitosamente
2. IoT Rule está habilitada en AWS Console
3. CloudWatch Logs de IoT Rule no muestra errores
4. Policy permite publish en `kia/paintshop/*`

**Comandos de diagnóstico:**
```bash
# Ver logs de IoT Rule
aws logs tail /aws/iot/rules/kia-paintshop-prototype --follow

# Verificar métricas de IoT Core
aws cloudwatch get-metric-statistics \
  --namespace AWS/IoT \
  --metric-name PublishIn.Success \
  --dimensions Name=Protocol,Value=MQTT \
  --start-time $(date -u -d '1 hour ago' --iso-8601) \
  --end-time $(date -u --iso-8601) \
  --period 3600 \
  --statistics Sum
```

## Siguiente Paso

Una vez que hayas verificado que el simulador funciona correctamente:

✅ **Checkpoint 5 completado**

Puedes proceder a:
- **Tarea 6**: Implementar Lambda de ingesta para procesar los mensajes de IoT Core
- **Tarea 7**: Implementar Lambda de procesamiento de alarmas
- **Tarea 8**: Implementar Lambda de estadísticas

## Notas Importantes

- **Costos**: El simulador genera ~97 mensajes cada 30 segundos = ~280,000 mensajes/mes
- **Free Tier**: AWS IoT Core incluye 500,000 mensajes/mes gratis
- **Monitoreo**: Revisa CloudWatch Logs regularmente para detectar errores
- **Seguridad**: Los certificados son sensibles, no los subas a Git (ya están en .gitignore)

## Documentación Relacionada

- `simulator/README.md` - Documentación completa del simulador
- `docs/IOT_SETUP.md` - Guía de configuración de IoT Core
- `terraform/IOT_CORE.md` - Detalles de la infraestructura IoT
- `simulator/config.yaml` - Configuración del simulador
