# Guía de Testing para Principiantes - Prototipo IoT Paint Shop KIA

**Para:** Estudiante de segundo semestre aprendiendo POO  
**Objetivo:** Validar que el prototipo MVP está listo para producción  
**Tiempo estimado:** 3-4 horas  
**Fecha:** 19 de febrero de 2026

---

## 📚 Tabla de Contenidos

1. [Introducción y Conceptos Básicos](#introducción)
2. [Requisitos Previos](#requisitos-previos)
3. [Fase 1: Preparación del Entorno](#fase-1-preparación)
4. [Fase 2: Despliegue de Infraestructura](#fase-2-infraestructura)
5. [Fase 3: Pruebas del Simulador](#fase-3-simulador)
6. [Fase 4: Pruebas del Backend](#fase-4-backend)
7. [Fase 5: Pruebas de la API](#fase-5-api)
8. [Fase 6: Pruebas del Dashboard](#fase-6-dashboard)
9. [Fase 7: Verificación de Costos](#fase-7-costos)
10. [Fase 8: Limpieza Final](#fase-8-limpieza)
11. [Checklist de Validación](#checklist)
12. [Glosario de Términos](#glosario)
13. [Solución de Problemas](#problemas)

---

## 🎯 Introducción

### ¿Qué vas a hacer?

Vas a probar un sistema completo que simula el monitoreo de 100 variables del proceso de pintura de KIA.
El sistema recoge datos de sensores simulados, los procesa, detecta alarmas y los muestra en un dashboard web.

### ¿Por qué es importante?

Necesitamos confirmar que:
- ✅ Todos los componentes funcionan correctamente
- ✅ Los datos fluyen desde el simulador hasta el dashboard
- ✅ Las alarmas se generan y se pueden reconocer
- ✅ Los costos están dentro del presupuesto ($50/mes)
- ✅ El sistema se puede eliminar completamente sin dejar recursos



---

## 📖 Conceptos Básicos (Nivel de Confianza para Investigar)

Antes de empezar, aquí están los conceptos clave. El "Nivel de Confianza" te indica qué tan importante es que investigues más sobre cada tema:

### 🔴 CRÍTICO - Debes entender bien antes de continuar

**AWS (Amazon Web Services)** 🔴
- **Qué es:** Plataforma de servicios en la nube de Amazon
- **Por qué importa:** Todo nuestro sistema corre en AWS
- **Investiga:** Qué es la nube, cómo funciona AWS, qué es una región de AWS
- **Tiempo:** 30 minutos de lectura

**API (Application Programming Interface)** 🔴
- **Qué es:** Forma en que dos programas se comunican entre sí
- **Por qué importa:** Nuestro dashboard se comunica con el backend a través de una API
- **Investiga:** Qué es una API REST, qué son los endpoints, qué es HTTP
- **Tiempo:** 20 minutos de lectura

**Terminal/Línea de Comandos** 🔴
- **Qué es:** Interfaz de texto para dar comandos a la computadora
- **Por qué importa:** Ejecutarás muchos comandos en la terminal
- **Investiga:** Comandos básicos (cd, ls, cat), qué es bash
- **Tiempo:** 15 minutos de práctica

### 🟡 IMPORTANTE - Deberías entender lo básico

**IoT (Internet of Things)** 🟡
- **Qué es:** Dispositivos conectados a internet que envían datos
- **Por qué importa:** Nuestro simulador actúa como un dispositivo IoT
- **Investiga:** Ejemplos de IoT, cómo se comunican los dispositivos
- **Tiempo:** 15 minutos de lectura

**MQTT (Message Queuing Telemetry Transport)** 🟡
- **Qué es:** Protocolo de comunicación ligero para IoT
- **Por qué importa:** El simulador usa MQTT para enviar datos
- **Investiga:** Qué es un protocolo, cómo funciona MQTT, qué son los topics
- **Tiempo:** 20 minutos de lectura

**DynamoDB** 🟡
- **Qué es:** Base de datos NoSQL de AWS
- **Por qué importa:** Aquí se guardan todos los datos del sistema
- **Investiga:** Diferencia entre SQL y NoSQL, qué es una tabla, qué es una clave
- **Tiempo:** 15 minutos de lectura

**Lambda (AWS Lambda)** 🟡
- **Qué es:** Servicio que ejecuta código sin necesidad de servidores
- **Por qué importa:** Nuestro backend usa 8 funciones Lambda
- **Investiga:** Qué es serverless, cómo funciona Lambda
- **Tiempo:** 15 minutos de lectura



### 🟢 OPCIONAL - Útil pero no crítico para las pruebas

**Terraform** 🟢
- **Qué es:** Herramienta para crear infraestructura con código
- **Por qué importa:** Usamos Terraform para crear todos los recursos en AWS
- **Investiga:** Qué es Infrastructure as Code (IaC)
- **Tiempo:** 10 minutos de lectura

**React** 🟢
- **Qué es:** Librería de JavaScript para crear interfaces de usuario
- **Por qué importa:** El dashboard está hecho con React
- **Investiga:** Qué es un componente, qué es JSX
- **Tiempo:** 10 minutos de lectura

**TypeScript** 🟢
- **Qué es:** JavaScript con tipos (más estricto)
- **Por qué importa:** El dashboard usa TypeScript
- **Investiga:** Diferencia entre JavaScript y TypeScript
- **Tiempo:** 10 minutos de lectura

---

## ✅ Requisitos Previos

### Software que Necesitas Instalar

Antes de empezar, verifica que tienes instalado:

#### 1. AWS CLI (Interfaz de Línea de Comandos de AWS)

```bash
# Verificar si está instalado
aws --version
```

**Resultado esperado:** `aws-cli/2.x.x` o superior

**Si no está instalado:**
- macOS: `brew install awscli`
- Documentación: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

#### 2. Terraform

```bash
# Verificar si está instalado
terraform --version
```

**Resultado esperado:** `Terraform v1.5.0` o superior

**Si no está instalado:**
- macOS: `brew install terraform`
- Documentación: https://developer.hashicorp.com/terraform/downloads

#### 3. Python 3.11+

```bash
# Verificar si está instalado
python3 --version
```

**Resultado esperado:** `Python 3.11.x` o superior

**Si no está instalado:**
- macOS: `brew install python@3.11`
- Documentación: https://www.python.org/downloads/



#### 4. Node.js y npm

```bash
# Verificar si están instalados
node --version
npm --version
```

**Resultado esperado:** Node v18+ y npm v9+

**Si no están instalados:**
- macOS: `brew install node`
- Documentación: https://nodejs.org/

#### 5. Cuenta de AWS Configurada

```bash
# Verificar que AWS CLI está configurado
aws sts get-caller-identity
```

**Resultado esperado:** Debe mostrar tu información de cuenta AWS (AccountId, UserId, Arn)

**Si no está configurado:**
```bash
aws configure
# Te pedirá:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (usa: us-east-1)
# - Default output format (usa: json)
```

**⚠️ IMPORTANTE:** Necesitas credenciales de AWS con permisos de administrador para crear recursos.

---

## 🚀 Fase 1: Preparación del Entorno

### Paso 1.1: Clonar el Repositorio (si no lo tienes)

```bash
# Navega a tu carpeta de proyectos
cd ~/Documents/proyectos

# Clona el repositorio (si aplica)
# git clone <url-del-repositorio>
# cd kia-paintshop-iot-prototype
```

**Nota:** Si ya tienes el proyecto, simplemente navega a la carpeta del proyecto.

### Paso 1.2: Instalar Dependencias de Python

```bash
# Crear entorno virtual (recomendado)
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

**Resultado esperado:** Todas las dependencias se instalan sin errores.

**Qué hace esto:**
- Crea un entorno aislado para las dependencias de Python
- Instala boto3 (SDK de AWS), paho-mqtt (cliente MQTT), hypothesis (testing), pytest (testing)



### Paso 1.3: Verificar Estructura del Proyecto

```bash
# Listar archivos principales
ls -la
```

**Deberías ver:**
- `terraform/` - Carpeta con configuración de infraestructura
- `simulator/` - Carpeta con el simulador de datos
- `lambdas/` - Carpeta con funciones Lambda
- `dashboard/` - Carpeta con el dashboard web
- `tests/` - Carpeta con pruebas
- `README.md` - Documentación principal
- `requirements.txt` - Dependencias de Python

**✅ Checklist Fase 1:**
- [ ] AWS CLI instalado y configurado
- [ ] Terraform instalado
- [ ] Python 3.11+ instalado
- [ ] Node.js y npm instalados
- [ ] Dependencias de Python instaladas
- [ ] Estructura del proyecto verificada

---

## 🏗️ Fase 2: Despliegue de Infraestructura

### ¿Qué vamos a hacer?

Vamos a crear todos los recursos en AWS usando Terraform. Esto incluye:
- 4 tablas de DynamoDB (bases de datos)
- 8 funciones Lambda (código que se ejecuta en la nube)
- 1 API Gateway (punto de entrada para la API)
- 1 configuración de IoT Core (para recibir datos del simulador)
- 1 bucket de S3 (almacenamiento de archivos)
- Configuración de CloudWatch (monitoreo)

**Tiempo estimado:** 30-45 minutos

### Paso 2.1: Limpiar Recursos Previos (si existen)

```bash
cd terraform

# Si ya desplegaste antes, destruye los recursos
terraform destroy -auto-approve
```

**Qué hace esto:** Elimina todos los recursos de AWS que se crearon previamente.

**Resultado esperado:** Si no hay recursos previos, verá un mensaje indicando que no hay nada que destruir.

### Paso 2.2: Inicializar Terraform

```bash
# Asegúrate de estar en la carpeta terraform
cd terraform

# Inicializar Terraform
terraform init
```

**Qué hace esto:** Descarga los plugins necesarios para que Terraform pueda comunicarse con AWS.

**Resultado esperado:**
```
Terraform has been successfully initialized!
```



### Paso 2.3: Planificar el Despliegue

```bash
# Crear un plan de lo que se va a crear
terraform plan -out=tfplan
```

**Qué hace esto:** Terraform analiza la configuración y te muestra qué recursos va a crear, sin crearlos todavía.

**Resultado esperado:**
```
Plan: 50+ to add, 0 to change, 0 to destroy.
```

**⚠️ IMPORTANTE:** Revisa el plan cuidadosamente. Deberías ver:
- 4 tablas de DynamoDB
- 8 funciones Lambda
- 1 API Gateway
- 1 Thing de IoT
- 1 bucket de S3
- Varios roles de IAM
- Log groups de CloudWatch

**Tiempo:** Este comando tarda 1-2 minutos.

### Paso 2.4: Aplicar el Despliegue

```bash
# Crear todos los recursos en AWS
terraform apply tfplan
```

**Qué hace esto:** Crea todos los recursos en AWS según el plan.

**Resultado esperado:**
```
Apply complete! Resources: 50+ added, 0 changed, 0 destroyed.

Outputs:

api_key = <sensitive>
api_url = "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/demo"
iot_endpoint = "xxxxxxxxxx-ats.iot.us-east-1.amazonaws.com"
```

**⏱️ Tiempo:** Este comando tarda 5-10 minutos. ¡Ten paciencia!

**🎉 ¡Felicidades!** Si llegaste aquí sin errores, has creado toda la infraestructura en AWS.

### Paso 2.5: Guardar los Outputs

```bash
# Guardar los outputs en un archivo
terraform output -json > ../terraform-outputs.json

# Ver los outputs importantes
terraform output api_url
terraform output api_key
terraform output iot_endpoint
```

**Qué hace esto:** Guarda información importante que necesitarás más adelante (URL de la API, clave de API, endpoint de IoT).

**⚠️ IMPORTANTE:** Copia estos valores en un lugar seguro. Los necesitarás para configurar el simulador y el dashboard.



### Paso 2.6: Verificar en la Consola de AWS (Opcional pero Recomendado)

Abre tu navegador y ve a https://console.aws.amazon.com

**DynamoDB:**
1. Busca "DynamoDB" en la barra de búsqueda
2. Haz clic en "Tables" (Tablas)
3. Deberías ver 4 tablas:
   - `kia-paintshop-prototype-demo-sensor-data`
   - `kia-paintshop-prototype-demo-alarms`
   - `kia-paintshop-prototype-demo-statistics`
   - `kia-paintshop-prototype-demo-variables-metadata`

**Lambda:**
1. Busca "Lambda" en la barra de búsqueda
2. Haz clic en "Functions" (Funciones)
3. Deberías ver 8 funciones Lambda con nombres que empiezan con `kia-paintshop`

**API Gateway:**
1. Busca "API Gateway" en la barra de búsqueda
2. Deberías ver una API llamada `kia-paintshop-api-demo`

**IoT Core:**
1. Busca "IoT Core" en la barra de búsqueda
2. Ve a "Manage" → "Things"
3. Deberías ver un Thing llamado `kia-paintshop-simulator-demo`

**✅ Checklist Fase 2:**
- [ ] `terraform init` ejecutado exitosamente
- [ ] `terraform plan` muestra 50+ recursos a crear
- [ ] `terraform apply` completado sin errores
- [ ] Outputs guardados (api_url, api_key, iot_endpoint)
- [ ] Recursos verificados en consola de AWS (opcional)

---

## 🎮 Fase 3: Pruebas del Simulador

### ¿Qué vamos a hacer?

El simulador es un programa en Python que simula 97 sensores del proceso de pintura. Genera datos cada 30 segundos y los envía a AWS IoT Core usando el protocolo MQTT.

**Tiempo estimado:** 15-20 minutos

### Paso 3.1: Descargar Certificados de IoT

Los certificados son como "llaves digitales" que permiten al simulador conectarse de forma segura a AWS IoT Core.

**Opción A: Descargar desde la Consola de AWS (Recomendado para principiantes)**

1. Ve a la consola de AWS IoT Core: https://console.aws.amazon.com/iot/
2. En el menú izquierdo, haz clic en "Security" → "Certificates"
3. Verás un certificado activo (con estado "Active")
4. Haz clic en el certificado
5. Descarga estos 3 archivos:
   - **Device certificate** → Guárdalo como `simulator/certs/device.crt`
   - **Private key** → Guárdalo como `simulator/certs/device.key`
   - **Amazon Root CA 1** → Guárdalo como `simulator/certs/AmazonRootCA1.pem`



**⚠️ IMPORTANTE:** Si no puedes descargar la clave privada (porque el certificado ya fue creado antes), necesitarás crear un nuevo certificado. Pide ayuda si esto sucede.

**Opción B: Descargar Root CA con comando**

```bash
cd simulator/certs
curl -o AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem
cd ../..
```

### Paso 3.2: Verificar que los Certificados Están en su Lugar

```bash
# Listar archivos en la carpeta de certificados
ls -la simulator/certs/
```

**Deberías ver:**
```
device.crt          (certificado del dispositivo)
device.key          (clave privada)
AmazonRootCA1.pem   (certificado raíz de Amazon)
```

### Paso 3.3: Configurar el Simulador

```bash
# Abrir el archivo de configuración
nano simulator/config.yaml
```

**O si prefieres un editor visual:**
```bash
code simulator/config.yaml
```

**Busca la sección `mqtt:` y actualiza el `endpoint`:**

```yaml
mqtt:
  endpoint: "TU_IOT_ENDPOINT_AQUI"  # Pega el valor de iot_endpoint que guardaste antes
  port: 8883
  cert_path: "certs/device.crt"
  key_path: "certs/device.key"
  ca_path: "certs/AmazonRootCA1.pem"
```

**Ejemplo:**
```yaml
mqtt:
  endpoint: "a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com"
  port: 8883
  cert_path: "certs/device.crt"
  key_path: "certs/device.key"
  ca_path: "certs/AmazonRootCA1.pem"
```

**Guarda el archivo:**
- En nano: Presiona `Ctrl+X`, luego `Y`, luego `Enter`
- En VS Code: `Cmd+S` (Mac) o `Ctrl+S` (Windows/Linux)

### Paso 3.4: Ejecutar el Simulador (Prueba de 2 Minutos)

```bash
# Asegúrate de estar en la carpeta raíz del proyecto
cd simulator

# Ejecutar el simulador
python simulator.py --config config.yaml
```

**Qué deberías ver:**

```
2026-02-19 10:30:00 - INFO - Simulator starting...
2026-02-19 10:30:00 - INFO - Loaded 97 variables from configuration
2026-02-19 10:30:01 - INFO - Connected to MQTT broker: xxxxx-ats.iot.us-east-1.amazonaws.com
2026-02-19 10:30:01 - INFO - Publishing data for 97 variables...
2026-02-19 10:30:01 - INFO - Published to kia/paintshop/pre-treatment/PT-TEMP-001
2026-02-19 10:30:01 - INFO - Published to kia/paintshop/pre-treatment/PT-TEMP-002
...
2026-02-19 10:30:31 - INFO - Cycle complete. 97 messages published.
```



**⏱️ Espera 2 minutos** para que el simulador complete al menos 4 ciclos (cada ciclo es de 30 segundos).

**Para detener el simulador:**
Presiona `Ctrl+C` en la terminal.

**✅ Señales de que funciona correctamente:**
- ✅ Mensaje "Connected to MQTT broker"
- ✅ Mensajes "Published to kia/paintshop/..."
- ✅ Mensaje "Cycle complete. 97 messages published"
- ✅ No hay errores de conexión

**❌ Señales de problemas:**
- ❌ "Connection refused" → Verifica el endpoint en config.yaml
- ❌ "SSL/TLS error" → Verifica que los certificados estén en la carpeta correcta
- ❌ "Authentication failed" → Verifica que el certificado esté activo en AWS

### Paso 3.5: Verificar que los Datos Llegaron a DynamoDB

```bash
# Consultar la tabla de datos de sensores
aws dynamodb scan \
  --table-name kia-paintshop-prototype-demo-sensor-data \
  --limit 5
```

**Qué deberías ver:**
Un JSON con al menos 5 items (registros). Cada item debe tener:
- `PK`: Clave de partición (ejemplo: `pre-treatment#PT-TEMP-001`)
- `SK`: Clave de ordenamiento (ejemplo: `DATA#1708340400000`)
- `variable_id`: ID de la variable (ejemplo: `PT-TEMP-001`)
- `timestamp`: Marca de tiempo ISO 8601
- `value`: Valor numérico
- `unit`: Unidad de medida (ejemplo: `°C`)

**Ejemplo de salida:**
```json
{
  "Items": [
    {
      "PK": {"S": "pre-treatment#PT-TEMP-001"},
      "SK": {"S": "DATA#1708340400000"},
      "variable_id": {"S": "PT-TEMP-001"},
      "timestamp": {"S": "2026-02-19T10:30:00.000Z"},
      "value": {"N": "65.3"},
      "unit": {"S": "°C"}
    }
  ],
  "Count": 5
}
```

**✅ Checklist Fase 3:**
- [ ] Certificados descargados y en la carpeta correcta
- [ ] config.yaml actualizado con el endpoint de IoT
- [ ] Simulador se conecta exitosamente
- [ ] Simulador publica mensajes cada 30 segundos
- [ ] Datos aparecen en DynamoDB

---

## 🔧 Fase 4: Pruebas del Backend

### ¿Qué vamos a hacer?

Vamos a verificar que las 3 funciones Lambda del backend están procesando los datos correctamente:
1. **Lambda Ingest:** Recibe datos de IoT Core y los guarda en DynamoDB
2. **Lambda Process:** Detecta anomalías y genera alarmas
3. **Lambda Statistics:** Calcula estadísticas cada 5 minutos

**Tiempo estimado:** 10-15 minutos



### Paso 4.1: Verificar Lambda Ingest (Ingesta de Datos)

```bash
# Ver los logs de la Lambda de ingesta
aws logs tail /aws/lambda/kia-paintshop-ingest-demo --since 5m
```

**Qué deberías ver:**
```
2026-02-19 10:30:01 INFO Received IoT message for variable: PT-TEMP-001
2026-02-19 10:30:01 INFO Validation successful
2026-02-19 10:30:01 INFO Stored in DynamoDB
2026-02-19 10:30:01 INFO Published to EventBridge
```

**Qué significa cada línea:**
- **Received IoT message:** La Lambda recibió un mensaje del simulador
- **Validation successful:** El mensaje tiene el formato correcto
- **Stored in DynamoDB:** Los datos se guardaron en la base de datos
- **Published to EventBridge:** Se envió un evento para que otras Lambdas lo procesen

### Paso 4.2: Verificar Lambda Process (Procesamiento de Alarmas)

```bash
# Ver los logs de la Lambda de procesamiento
aws logs tail /aws/lambda/kia-paintshop-process-demo --since 5m
```

**Qué deberías ver:**
```
2026-02-19 10:30:02 INFO Processing data for variable: PT-TEMP-001
2026-02-19 10:30:02 INFO Checking thresholds...
2026-02-19 10:30:02 INFO No alarm condition detected
```

**O si hay una alarma:**
```
2026-02-19 10:30:02 INFO Alarm generated: Temperature exceeds high threshold
2026-02-19 10:30:02 INFO Severity: warning
2026-02-19 10:30:02 INFO Alarm stored in DynamoDB
```

### Paso 4.3: Generar una Alarma de Prueba (Opcional)

Si quieres ver cómo se genera una alarma, puedes modificar temporalmente el simulador para generar valores fuera de rango.

**⚠️ AVANZADO:** Solo haz esto si te sientes cómoda editando código Python.

```bash
# Editar el generador de datos
nano simulator/data_generator.py
```

Busca la línea que dice `anomaly_probability = 0.05` y cámbiala a `anomaly_probability = 1.0` (esto hará que TODOS los valores sean anomalías).

Guarda, ejecuta el simulador por 1 minuto, y luego revierte el cambio.

### Paso 4.4: Verificar Alarmas en DynamoDB

```bash
# Consultar la tabla de alarmas
aws dynamodb scan \
  --table-name kia-paintshop-prototype-demo-alarms \
  --limit 5
```

**Si hay alarmas, deberías ver:**
```json
{
  "Items": [
    {
      "alarm_id": {"S": "uuid-aqui"},
      "variable_id": {"S": "PT-TEMP-001"},
      "severity": {"S": "warning"},
      "status": {"S": "active"},
      "value": {"N": "69.5"},
      "threshold": {"N": "68.0"},
      "created_at": {"S": "2026-02-19T10:30:00.000Z"}
    }
  ]
}
```



### Paso 4.5: Verificar Lambda Statistics (Estadísticas)

Esta Lambda se ejecuta automáticamente cada 5 minutos. Espera al menos 5 minutos después de iniciar el simulador.

```bash
# Ver los logs de la Lambda de estadísticas
aws logs tail /aws/lambda/kia-paintshop-statistics-demo --since 10m
```

**Qué deberías ver:**
```
2026-02-19 10:35:00 INFO Starting statistics calculation
2026-02-19 10:35:01 INFO Calculated statistics for PT-TEMP-001: avg=65.3, min=64.1, max=66.8
2026-02-19 10:35:05 INFO Statistics stored in DynamoDB
```

```bash
# Verificar estadísticas en DynamoDB
aws dynamodb scan \
  --table-name kia-paintshop-prototype-demo-statistics \
  --limit 5
```

**Deberías ver estadísticas calculadas:**
```json
{
  "Items": [
    {
      "variable_id": {"S": "PT-TEMP-001"},
      "window_start": {"S": "2026-02-19T10:25:00.000Z"},
      "window_end": {"S": "2026-02-19T10:35:00.000Z"},
      "avg": {"N": "65.3"},
      "min": {"N": "64.1"},
      "max": {"N": "66.8"},
      "stddev": {"N": "0.8"},
      "count": {"N": "20"}
    }
  ]
}
```

**✅ Checklist Fase 4:**
- [ ] Lambda Ingest procesa mensajes correctamente
- [ ] Datos se guardan en DynamoDB
- [ ] Lambda Process detecta anomalías (si las hay)
- [ ] Alarmas se guardan en DynamoDB (si se generan)
- [ ] Lambda Statistics calcula estadísticas cada 5 minutos
- [ ] Estadísticas se guardan en DynamoDB

---

## 🌐 Fase 5: Pruebas de la API

### ¿Qué vamos a hacer?

Vamos a probar los 5 endpoints de la API REST usando el comando `curl`. La API es la forma en que el dashboard se comunica con el backend.

**Tiempo estimado:** 15-20 minutos

### Paso 5.1: Configurar Variables de Entorno

```bash
# Volver a la carpeta raíz del proyecto
cd ..

# Configurar variables de entorno
export API_URL=$(cd terraform && terraform output -raw api_url)
export API_KEY=$(cd terraform && terraform output -raw api_key)

# Verificar que se configuraron correctamente
echo "API URL: $API_URL"
echo "API Key: $API_KEY"
```

**Deberías ver:**
```
API URL: https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/demo
API Key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```



### Paso 5.2: Probar GET /variables (Listar Variables)

Este endpoint devuelve la lista de las 97 variables del sistema.

```bash
curl -X GET "$API_URL/variables" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" | jq
```

**Qué hace este comando:**
- `curl`: Herramienta para hacer peticiones HTTP
- `-X GET`: Tipo de petición (GET = obtener datos)
- `-H "x-api-key: $API_KEY"`: Envía la clave de API para autenticación
- `| jq`: Formatea el JSON para que sea más fácil de leer

**Resultado esperado:**
```json
{
  "success": true,
  "data": {
    "variables": [
      {
        "variable_id": "PT-TEMP-001",
        "name": "Pre-Treatment Temperature 1",
        "area": "pre-treatment",
        "unit": "°C",
        "min_range": 60.0,
        "max_range": 70.0,
        "alarm_low": 62.0,
        "alarm_high": 68.0
      },
      ...más variables...
    ],
    "total": 97
  },
  "timestamp": "2026-02-19T10:30:00.000Z"
}
```

**✅ Qué verificar:**
- `"success": true` → La petición fue exitosa
- `"total": 97` → Hay 97 variables en el sistema
- Cada variable tiene: variable_id, name, area, unit, rangos y umbrales

### Paso 5.3: Probar GET /variables/{id}/data (Obtener Datos de una Variable)

Este endpoint devuelve los datos históricos de una variable específica.

```bash
# Calcular timestamps (última hora)
START_TIME=$(date -u -v-1H +"%Y-%m-%dT%H:%M:%SZ")  # macOS
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Hacer la petición
curl -X GET "$API_URL/variables/PT-TEMP-001/data?start=$START_TIME&end=$END_TIME" \
  -H "x-api-key: $API_KEY" | jq
```

**Nota para Linux:** Si estás en Linux, usa este comando para calcular timestamps:
```bash
START_TIME=$(date -u -d '1 hour ago' +"%Y-%m-%dT%H:%M:%SZ")
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
```

**Resultado esperado:**
```json
{
  "success": true,
  "data": {
    "variable_id": "PT-TEMP-001",
    "data_points": [
      {
        "timestamp": "2026-02-19T10:30:00.000Z",
        "value": 65.3,
        "unit": "°C",
        "quality": "good"
      },
      ...más puntos de datos...
    ],
    "count": 120
  }
}
```

**✅ Qué verificar:**
- `"success": true`
- `"count"` debería ser mayor a 0 (si el simulador ha estado corriendo)
- Cada punto de datos tiene: timestamp, value, unit



### Paso 5.4: Probar GET /alarms (Listar Alarmas)

Este endpoint devuelve las alarmas activas del sistema.

```bash
curl -X GET "$API_URL/alarms?status=active" \
  -H "x-api-key: $API_KEY" | jq
```

**Resultado esperado (si hay alarmas):**
```json
{
  "success": true,
  "data": {
    "alarms": [
      {
        "alarm_id": "uuid-aqui",
        "variable_id": "PT-TEMP-001",
        "area": "pre-treatment",
        "severity": "warning",
        "status": "active",
        "message": "Temperature exceeds high threshold",
        "value": 69.5,
        "threshold": 68.0,
        "created_at": "2026-02-19T10:30:00.000Z"
      }
    ],
    "total": 1
  }
}
```

**Resultado esperado (si NO hay alarmas):**
```json
{
  "success": true,
  "data": {
    "alarms": [],
    "total": 0
  }
}
```

**✅ Ambos resultados son válidos.** Si no hay alarmas, significa que todos los valores están dentro de los umbrales normales.

### Paso 5.5: Probar POST /alarms/{id}/acknowledge (Reconocer Alarma)

**⚠️ Solo puedes hacer esto si hay al menos una alarma activa.**

Si tienes una alarma del paso anterior, copia su `alarm_id` y úsalo aquí:

```bash
# Reemplaza ALARM_ID_AQUI con el ID real de una alarma
ALARM_ID="ALARM_ID_AQUI"

curl -X POST "$API_URL/alarms/$ALARM_ID/acknowledge" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" | jq
```

**Resultado esperado:**
```json
{
  "success": true,
  "data": {
    "alarm_id": "uuid-aqui",
    "status": "acknowledged",
    "acknowledged_at": "2026-02-19T10:35:00.000Z"
  }
}
```

**✅ Qué verificar:**
- `"success": true`
- `"status": "acknowledged"` → La alarma cambió de estado
- `"acknowledged_at"` tiene una fecha/hora

### Paso 5.6: Probar GET /statistics/{variable_id} (Obtener Estadísticas)

Este endpoint devuelve las estadísticas calculadas para una variable.

```bash
curl -X GET "$API_URL/statistics/PT-TEMP-001" \
  -H "x-api-key: $API_KEY" | jq
```

**Resultado esperado:**
```json
{
  "success": true,
  "data": {
    "variable_id": "PT-TEMP-001",
    "statistics": [
      {
        "window_start": "2026-02-19T10:25:00.000Z",
        "window_end": "2026-02-19T10:35:00.000Z",
        "window_minutes": 10,
        "count": 20,
        "avg": 65.3,
        "min": 64.1,
        "max": 66.8,
        "stddev": 0.8
      }
    ]
  }
}
```

**✅ Qué verificar:**
- `"success": true`
- Hay al menos una ventana de estadísticas
- Los valores de avg, min, max, stddev son números razonables



### Paso 5.7: Probar Autenticación (Debe Fallar sin API Key)

Vamos a verificar que la API está protegida correctamente.

```bash
# Intentar acceder SIN la API key (debe fallar)
curl -X GET "$API_URL/variables" \
  -H "Content-Type: application/json"
```

**Resultado esperado (ERROR 401):**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing or invalid API key"
  }
}
```

**✅ Esto es BUENO.** Significa que la API está protegida y requiere autenticación.

**✅ Checklist Fase 5:**
- [ ] GET /variables devuelve 97 variables
- [ ] GET /variables/{id}/data devuelve datos históricos
- [ ] GET /alarms devuelve alarmas (o lista vacía)
- [ ] POST /alarms/{id}/acknowledge actualiza el estado (si hay alarmas)
- [ ] GET /statistics/{variable_id} devuelve estadísticas
- [ ] API rechaza peticiones sin API key (401 Unauthorized)

---

## 🖥️ Fase 6: Pruebas del Dashboard

### ¿Qué vamos a hacer?

Vamos a iniciar el dashboard web (interfaz visual) y verificar que muestra los datos correctamente.

**Tiempo estimado:** 20-30 minutos

### Paso 6.1: Configurar Variables de Entorno del Dashboard

```bash
cd dashboard

# Crear archivo .env con las credenciales
cat > .env << EOF
REACT_APP_API_URL=$API_URL
REACT_APP_API_KEY=$API_KEY
EOF

# Verificar que se creó correctamente
cat .env
```

**Deberías ver:**
```
REACT_APP_API_URL=https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/demo
REACT_APP_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Paso 6.2: Instalar Dependencias del Dashboard

```bash
# Instalar todas las dependencias de Node.js
npm install
```

**Qué hace esto:** Descarga todas las librerías que el dashboard necesita (React, TypeScript, Recharts, etc.).

**⏱️ Tiempo:** Este comando puede tardar 2-5 minutos.

**Resultado esperado:**
```
added 1500+ packages in 3m
```

**⚠️ Advertencias:** Es normal ver algunas advertencias sobre vulnerabilidades. No te preocupes por ahora.



### Paso 6.3: Iniciar el Servidor de Desarrollo

```bash
npm start
```

**Qué hace esto:** Inicia un servidor web local y abre el dashboard en tu navegador.

**Resultado esperado:**
```
Compiled successfully!

You can now view dashboard in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.
```

**🎉 Tu navegador debería abrirse automáticamente** en http://localhost:3000

**Si no se abre automáticamente:** Abre tu navegador y ve a http://localhost:3000

### Paso 6.4: Verificar Componentes del Dashboard

Ahora vas a verificar visualmente cada componente del dashboard. Usa esta lista como checklist:

#### ✅ Componente: VariableList (Lista de Variables)

**Ubicación:** Panel izquierdo del dashboard

**Qué verificar:**
- [ ] Se muestran aproximadamente 97 variables
- [ ] Las variables están organizadas por área:
  - Pre-Treatment (48 variables)
  - E-Coat (18 variables)
  - Production Control (31 variables)
- [ ] Cada variable muestra:
  - ID (ejemplo: PT-TEMP-001)
  - Nombre descriptivo
  - Valor actual
  - Unidad de medida (°C, pH, etc.)
- [ ] Puedes hacer clic en una variable para seleccionarla
- [ ] Las variables con alarmas tienen un indicador visual (color rojo o amarillo)

**📸 Toma una captura de pantalla** de la lista de variables para tu reporte.

#### ✅ Componente: VariableChart (Gráfico de Variable)

**Ubicación:** Panel central del dashboard

**Qué verificar:**
- [ ] Al seleccionar una variable, aparece un gráfico de línea
- [ ] El gráfico muestra los últimos 60 minutos de datos
- [ ] El eje X muestra timestamps (fechas/horas)
- [ ] El eje Y muestra valores con la unidad correcta
- [ ] Se ven líneas horizontales de umbrales:
  - Línea roja superior (alarm_high)
  - Línea roja inferior (alarm_low)
- [ ] El gráfico se actualiza automáticamente cada 30 segundos
- [ ] Mientras carga, se muestra un spinner o indicador de carga

**📸 Toma una captura de pantalla** del gráfico mostrando datos.

#### ✅ Componente: AlarmPanel (Panel de Alarmas)

**Ubicación:** Panel superior derecho

**Qué verificar:**
- [ ] Se muestra el panel de alarmas
- [ ] Si hay alarmas activas, se muestran con:
  - ID de la variable
  - Severidad (warning = amarillo, critical = rojo)
  - Mensaje descriptivo
  - Valor que causó la alarma
  - Umbral que se excedió
  - Fecha/hora de creación
- [ ] Cada alarma tiene un botón "Acknowledge" (Reconocer)
- [ ] Al hacer clic en "Acknowledge", la alarma cambia de estado
- [ ] Puedes filtrar alarmas por estado: active, acknowledged, resolved
- [ ] Si no hay alarmas, se muestra un mensaje como "No active alarms"

**📸 Toma una captura de pantalla** del panel de alarmas (con o sin alarmas).



#### ✅ Componente: StatisticsCard (Tarjeta de Estadísticas)

**Ubicación:** Panel inferior derecho

**Qué verificar:**
- [ ] Se muestran estadísticas para la variable seleccionada
- [ ] Las estadísticas incluyen:
  - Promedio (Average)
  - Mínimo (Min)
  - Máximo (Max)
  - Desviación estándar (Std Dev)
- [ ] Los números tienen el formato correcto (2 decimales)
- [ ] Se muestra la unidad de medida
- [ ] Las estadísticas se actualizan cada 30 segundos

**📸 Toma una captura de pantalla** de las estadísticas.

#### ✅ Componente: ConnectionStatus (Estado de Conexión)

**Ubicación:** Esquina superior derecha

**Qué verificar:**
- [ ] Se muestra un indicador de estado de conexión
- [ ] Cuando está conectado: indicador verde con texto "Connected"
- [ ] Si hay error: indicador rojo con texto "Disconnected" o "Error"
- [ ] El indicador refleja el estado real de la API

### Paso 6.5: Probar Actualización Automática

**Objetivo:** Verificar que el dashboard se actualiza automáticamente cada 30 segundos.

**Cómo hacerlo:**
1. Asegúrate de que el simulador está corriendo
2. Selecciona una variable en el dashboard
3. Observa el gráfico
4. Espera 30 segundos
5. Deberías ver que aparece un nuevo punto de datos en el gráfico

**✅ Qué verificar:**
- [ ] El gráfico se actualiza sin necesidad de refrescar la página
- [ ] Los nuevos datos aparecen suavemente (sin parpadeos)
- [ ] El indicador de carga aparece brevemente durante la actualización

### Paso 6.6: Probar Flujo de Alarmas (Si hay alarmas)

**Objetivo:** Verificar el flujo completo de reconocimiento de alarmas.

**Cómo hacerlo:**
1. Si hay una alarma activa en el panel de alarmas
2. Haz clic en el botón "Acknowledge"
3. Espera 30 segundos para que el dashboard se actualice
4. La alarma debería moverse a la sección "Acknowledged"

**✅ Qué verificar:**
- [ ] El botón "Acknowledge" funciona
- [ ] La alarma cambia de estado
- [ ] El cambio se refleja en el dashboard después de 30 segundos

### Paso 6.7: Verificar Consola del Navegador (Opcional pero Recomendado)

**Cómo hacerlo:**
1. En tu navegador, presiona `F12` o `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows/Linux)
2. Ve a la pestaña "Console"
3. Busca errores (texto en rojo)

**✅ Qué verificar:**
- [ ] No hay errores críticos en rojo
- [ ] Puede haber advertencias en amarillo (es normal)
- [ ] No hay mensajes de "Failed to fetch" o "Network error"

**📸 Toma una captura de pantalla** de la consola si hay errores.

**✅ Checklist Fase 6:**
- [ ] Dashboard se inicia sin errores de compilación
- [ ] VariableList muestra 97 variables organizadas por área
- [ ] VariableChart muestra gráfico con datos históricos
- [ ] AlarmPanel muestra alarmas (o mensaje de "no alarms")
- [ ] StatisticsCard muestra estadísticas calculadas
- [ ] ConnectionStatus muestra estado "Connected"
- [ ] Dashboard se actualiza automáticamente cada 30 segundos
- [ ] Botón "Acknowledge" funciona (si hay alarmas)
- [ ] No hay errores críticos en la consola del navegador


---

## 💰 Fase 7: Verificación de Costos

### ¿Qué vamos a hacer?

Vamos a verificar que los costos del sistema están dentro del presupuesto de $50/mes. Este es uno de los requisitos más importantes del proyecto.

**Tiempo estimado:** 10-15 minutos

### Paso 7.1: Ejecutar Script de Verificación de Costos

```bash
# Volver a la carpeta raíz del proyecto
cd ..

# Ejecutar el script de verificación de costos
bash scripts/check_costs.sh
```

**Qué hace este script:**
- Consulta AWS Cost Explorer para obtener los costos actuales
- Muestra un desglose por servicio
- Compara con el presupuesto de $50/mes
- Muestra advertencias si se acerca a los límites

**Resultado esperado:**
```
=== AWS Cost Analysis ===
Period: Last 7 days

Service Breakdown:
- IoT Core:        $0.15
- Lambda:          $0.05
- DynamoDB:        $0.10
- API Gateway:     $0.03
- S3:              $0.01
- CloudWatch:      $0.02
------------------------
Total (7 days):    $0.36
Projected (30 days): $1.54

Budget: $50.00/month
Status: ✅ WITHIN BUDGET (3% used)
```

### Paso 7.2: Verificar Costos en la Consola de AWS

**Opción visual para verificar costos:**

1. Ve a la consola de AWS: https://console.aws.amazon.com
2. En la barra de búsqueda, escribe "Cost Explorer"
3. Haz clic en "Cost Explorer"
4. Si es tu primera vez, haz clic en "Enable Cost Explorer" (puede tardar 24 horas en activarse)
5. Una vez activado, ve a "Cost Explorer" → "Reports"
6. Selecciona "Last 7 days" en el rango de fechas
7. Agrupa por "Service" para ver el desglose

**Qué deberías ver:**
- Un gráfico de barras mostrando los costos por servicio
- Los servicios más costosos deberían ser:
  1. IoT Core (mensajes MQTT)
  2. DynamoDB (almacenamiento y operaciones)
  3. Lambda (invocaciones)
  4. API Gateway (requests)

**✅ Qué verificar:**
- [ ] El costo total de los últimos 7 días es menor a $2
- [ ] El costo proyectado para 30 días es menor a $10
- [ ] No hay servicios con costos inesperadamente altos
- [ ] IoT Core es el servicio más costoso (esto es normal)

**📸 Toma una captura de pantalla** del Cost Explorer para tu reporte.

### Paso 7.3: Entender el Desglose de Costos

**IoT Core (~$0.15/semana):**
- Costo por mensaje: $1.00 por millón de mensajes
- Nuestro uso: 97 variables × 2 mensajes/minuto × 60 min × 24 hrs × 7 días = ~195,000 mensajes/semana
- Costo: ~$0.20/semana

**DynamoDB (~$0.10/semana):**
- Modo on-demand: Pagas solo por lo que usas
- Escrituras: $1.25 por millón de unidades de escritura
- Lecturas: $0.25 por millón de unidades de lectura
- Almacenamiento: $0.25 por GB/mes
- Nuestro uso es mínimo porque usamos TTL para eliminar datos antiguos

**Lambda (~$0.05/semana):**
- Primeras 1 millón de invocaciones gratis cada mes
- Después: $0.20 por millón de invocaciones
- Nuestro uso: ~200,000 invocaciones/semana (dentro del tier gratuito)

**API Gateway (~$0.03/semana):**
- $3.50 por millón de requests
- Nuestro uso: ~10,000 requests/semana (dashboard polling cada 30s)

**S3 (~$0.01/semana):**
- Almacenamiento: $0.023 por GB/mes
- Nuestro uso: Casi nada porque archivamos poco

**CloudWatch (~$0.02/semana):**
- Logs: $0.50 por GB ingerido
- Métricas custom: $0.30 por métrica/mes
- Nuestro uso: Logs con retención de 7 días

### Paso 7.4: Configurar Alarma de Presupuesto (Opcional pero Recomendado)

**Para evitar sorpresas, configura una alarma de presupuesto:**

1. Ve a AWS Budgets: https://console.aws.amazon.com/billing/home#/budgets
2. Haz clic en "Create budget"
3. Selecciona "Cost budget"
4. Configura:
   - Budget name: `kia-paintshop-budget`
   - Period: Monthly
   - Budgeted amount: $50.00
5. En "Alert threshold":
   - Threshold: 80% (te avisará cuando llegues a $40)
   - Email: Tu correo electrónico
6. Haz clic en "Create budget"

**Ahora recibirás un email si los costos superan $40/mes.**

**✅ Checklist Fase 7:**
- [ ] Script check_costs.sh ejecutado exitosamente
- [ ] Costo total de 7 días es menor a $2
- [ ] Costo proyectado de 30 días es menor a $10
- [ ] Desglose de costos revisado en Cost Explorer
- [ ] Alarma de presupuesto configurada (opcional)

---

## 🧹 Fase 8: Limpieza Final

### ¿Qué vamos a hacer?

Vamos a eliminar TODOS los recursos de AWS para evitar costos innecesarios. Esta es una de las características más importantes del proyecto: debe ser completamente efímero.

**Tiempo estimado:** 15-20 minutos

**⚠️ IMPORTANTE:** Solo haz esto cuando hayas terminado TODAS las pruebas y hayas tomado todas las capturas de pantalla necesarias.

### Paso 8.1: Detener el Simulador y el Dashboard

```bash
# Si el simulador está corriendo, presiona Ctrl+C en su terminal

# Si el dashboard está corriendo, presiona Ctrl+C en su terminal
```

**Verifica que ambos procesos se detuvieron correctamente.**

### Paso 8.2: Ejecutar Script de Teardown

```bash
# Volver a la carpeta raíz del proyecto
cd ..

# Ejecutar el script de teardown
bash scripts/teardown.sh
```

**Qué hace este script:**
1. Detiene el simulador (si está corriendo)
2. Ejecuta `terraform destroy` para eliminar todos los recursos
3. Verifica que no queden recursos huérfanos
4. Muestra un resumen de lo que se eliminó

**Resultado esperado:**
```
=== KIA Paint Shop Teardown ===

Step 1: Stopping simulator...
✅ Simulator stopped

Step 2: Destroying Terraform resources...
This will destroy 50+ resources. Proceed? (yes/no): yes

Destroying resources...
[... muchas líneas de output ...]

Destroy complete! Resources: 50 destroyed.

Step 3: Verifying cleanup...
✅ No DynamoDB tables found
✅ No Lambda functions found
✅ No IoT Things found
✅ No S3 buckets found
✅ No API Gateways found

=== Teardown Complete ===
All resources have been successfully removed.
```

**⏱️ Tiempo:** Este proceso tarda 5-10 minutos.

### Paso 8.3: Ejecutar Script de Verificación de Limpieza

```bash
# Ejecutar el script de verificación
bash scripts/verify_cleanup.sh
```

**Qué hace este script:**
- Verifica que no queden recursos de AWS con el prefijo `kia-paintshop`
- Busca en todos los servicios: DynamoDB, Lambda, IoT, S3, API Gateway, CloudWatch
- Reporta cualquier recurso que no se haya eliminado

**Resultado esperado:**
```
=== Cleanup Verification ===

Checking DynamoDB tables...
✅ No tables found with prefix 'kia-paintshop'

Checking Lambda functions...
✅ No functions found with prefix 'kia-paintshop'

Checking IoT Things...
✅ No things found with prefix 'kia-paintshop'

Checking IoT Certificates...
✅ No active certificates found

Checking S3 buckets...
✅ No buckets found with prefix 'kia-paintshop'

Checking API Gateways...
✅ No APIs found with name 'kia-paintshop'

Checking CloudWatch Log Groups...
✅ No log groups found with prefix '/aws/lambda/kia-paintshop'

=== Verification Complete ===
✅ All resources have been successfully removed.
No residual charges expected.
```

**✅ Esto es lo que queremos ver:** Todos los checks en verde.

### Paso 8.4: Verificar Manualmente en la Consola de AWS (Recomendado)

**Para estar 100% segura, verifica manualmente en la consola:**

**DynamoDB:**
1. Ve a https://console.aws.amazon.com/dynamodb
2. Haz clic en "Tables"
3. Busca tablas con "kia-paintshop" en el nombre
4. **Resultado esperado:** No deberías ver ninguna tabla

**Lambda:**
1. Ve a https://console.aws.amazon.com/lambda
2. Haz clic en "Functions"
3. Busca funciones con "kia-paintshop" en el nombre
4. **Resultado esperado:** No deberías ver ninguna función

**IoT Core:**
1. Ve a https://console.aws.amazon.com/iot
2. Ve a "Manage" → "Things"
3. Busca things con "kia-paintshop" en el nombre
4. **Resultado esperado:** No deberías ver ningún thing
5. Ve a "Security" → "Certificates"
6. **Resultado esperado:** No deberías ver certificados activos relacionados

**S3:**
1. Ve a https://console.aws.amazon.com/s3
2. Busca buckets con "kia-paintshop" en el nombre
3. **Resultado esperado:** No deberías ver ningún bucket

**API Gateway:**
1. Ve a https://console.aws.amazon.com/apigateway
2. Busca APIs con "kia-paintshop" en el nombre
3. **Resultado esperado:** No deberías ver ninguna API

### Paso 8.5: Verificar Costos Finales (Después de 24 horas)

**⏰ Espera 24 horas después del teardown** y luego verifica:

```bash
# Verificar costos finales
bash scripts/check_costs.sh
```

**Resultado esperado:**
- Los costos deberían dejar de incrementarse después del teardown
- Puede haber un pequeño cargo residual por los datos que se procesaron antes del teardown
- El costo total del proyecto debería ser menor a $5

**✅ Checklist Fase 8:**
- [ ] Simulador detenido
- [ ] Dashboard detenido
- [ ] Script teardown.sh ejecutado exitosamente
- [ ] Script verify_cleanup.sh muestra todos los checks en verde
- [ ] Verificación manual en consola de AWS: no hay recursos
- [ ] Costos finales verificados después de 24 horas

---

## ✅ Checklist de Validación Final

Usa este checklist para confirmar que completaste todas las pruebas:

### Infraestructura
- [ ] Terraform inicializado correctamente
- [ ] 50+ recursos creados en AWS
- [ ] Outputs guardados (api_url, api_key, iot_endpoint)
- [ ] Recursos verificados en consola de AWS

### Simulador
- [ ] Certificados IoT descargados y configurados
- [ ] config.yaml actualizado con endpoint correcto
- [ ] Simulador se conecta a IoT Core exitosamente
- [ ] Simulador publica 97 variables cada 30 segundos
- [ ] Datos aparecen en DynamoDB tabla sensor-data

### Backend (Lambdas)
- [ ] Lambda Ingest procesa mensajes correctamente
- [ ] Lambda Process detecta anomalías y genera alarmas
- [ ] Lambda Statistics calcula estadísticas cada 5 minutos
- [ ] Logs de CloudWatch muestran ejecuciones exitosas
- [ ] No hay errores críticos en los logs

### API REST
- [ ] GET /variables devuelve 97 variables
- [ ] GET /variables/{id}/data devuelve datos históricos
- [ ] GET /alarms devuelve alarmas (o lista vacía)
- [ ] POST /alarms/{id}/acknowledge actualiza estado de alarma
- [ ] GET /statistics/{variable_id} devuelve estadísticas
- [ ] API rechaza peticiones sin API key (401)

### Dashboard
- [ ] Dashboard se inicia sin errores
- [ ] VariableList muestra 97 variables organizadas por área
- [ ] VariableChart muestra gráfico con datos en tiempo real
- [ ] AlarmPanel muestra alarmas activas
- [ ] StatisticsCard muestra estadísticas calculadas
- [ ] ConnectionStatus muestra "Connected"
- [ ] Auto-refresh funciona cada 30 segundos
- [ ] Botón "Acknowledge" funciona correctamente

### Costos
- [ ] Script check_costs.sh ejecutado
- [ ] Costo de 7 días es menor a $2
- [ ] Costo proyectado de 30 días es menor a $10
- [ ] Desglose de costos revisado
- [ ] Alarma de presupuesto configurada (opcional)

### Limpieza
- [ ] Script teardown.sh ejecutado exitosamente
- [ ] Script verify_cleanup.sh muestra todos los checks en verde
- [ ] Verificación manual: no hay recursos en AWS
- [ ] Costos finales verificados después de 24 horas

### Documentación
- [ ] Capturas de pantalla tomadas de cada componente
- [ ] Logs importantes guardados
- [ ] Notas de problemas encontrados (si los hubo)
- [ ] Reporte final preparado

---

## 📖 Glosario de Términos

### Términos de AWS

**AWS (Amazon Web Services)**
Plataforma de servicios en la nube de Amazon. Ofrece más de 200 servicios diferentes.

**Region (Región)**
Ubicación geográfica donde AWS tiene centros de datos. Ejemplo: us-east-1 (Virginia del Norte).

**IAM (Identity and Access Management)**
Servicio para gestionar permisos y accesos en AWS.

**DynamoDB**
Base de datos NoSQL de AWS. Almacena datos en tablas sin esquema fijo.

**Lambda**
Servicio serverless que ejecuta código sin necesidad de gestionar servidores.

**IoT Core**
Servicio de AWS para conectar dispositivos IoT a la nube.

**S3 (Simple Storage Service)**
Servicio de almacenamiento de archivos en la nube.

**API Gateway**
Servicio para crear, publicar y gestionar APIs REST.

**CloudWatch**
Servicio de monitoreo y logging de AWS.

**EventBridge**
Servicio de bus de eventos para comunicación entre servicios.

### Términos de IoT

**IoT (Internet of Things)**
Red de dispositivos físicos conectados a internet que recopilan e intercambian datos.

**MQTT (Message Queuing Telemetry Transport)**
Protocolo de comunicación ligero diseñado para IoT.

**Topic**
Canal de comunicación en MQTT. Ejemplo: `kia/paintshop/pre-treatment/PT-TEMP-001`

**X.509 Certificate**
Certificado digital usado para autenticación segura.

**TLS (Transport Layer Security)**
Protocolo de seguridad para comunicaciones encriptadas.

### Términos de Desarrollo

**API (Application Programming Interface)**
Conjunto de reglas que permiten que dos aplicaciones se comuniquen.

**REST (Representational State Transfer)**
Estilo de arquitectura para APIs web. Usa HTTP y métodos como GET, POST, PUT, DELETE.

**Endpoint**
URL específica de una API. Ejemplo: `/variables` o `/alarms`

**JSON (JavaScript Object Notation)**
Formato de texto para intercambiar datos. Ejemplo: `{"name": "value"}`

**HTTP Status Codes**
Códigos numéricos que indican el resultado de una petición:
- 200: OK (éxito)
- 400: Bad Request (petición incorrecta)
- 401: Unauthorized (no autorizado)
- 404: Not Found (no encontrado)
- 500: Internal Server Error (error del servidor)

**Serverless**
Arquitectura donde no gestionas servidores. AWS se encarga de todo.

**Infrastructure as Code (IaC)**
Gestionar infraestructura usando código (Terraform, CloudFormation).

**TTL (Time To Live)**
Tiempo de vida de un dato antes de ser eliminado automáticamente.

### Términos de Testing

**Unit Test**
Prueba que verifica una función o componente específico de forma aislada.

**Property-Based Test**
Prueba que verifica propiedades universales con datos generados aleatoriamente.

**Mock**
Objeto simulado que imita el comportamiento de un objeto real para testing.

**Assertion**
Verificación de que un valor es el esperado. Ejemplo: `assert x == 5`

**Coverage**
Porcentaje de código que está cubierto por tests.

### Términos del Proyecto

**Variable**
Sensor o medición del proceso de pintura. Ejemplo: temperatura, pH, presión.

**Alarm (Alarma)**
Notificación generada cuando una variable excede sus umbrales.

**Threshold (Umbral)**
Valor límite que no debe ser excedido. Ejemplo: temperatura máxima de 68°C.

**Severity (Severidad)**
Nivel de importancia de una alarma: warning (advertencia) o critical (crítico).

**Acknowledge (Reconocer)**
Marcar una alarma como vista/atendida por un operador.

**Dashboard**
Interfaz visual para monitorear variables y alarmas en tiempo real.

---

## 🔧 Solución de Problemas Comunes

### Problema 1: "terraform: command not found"

**Causa:** Terraform no está instalado o no está en el PATH.

**Solución:**
```bash
# macOS
brew install terraform

# Verificar instalación
terraform --version
```

### Problema 2: "aws: command not found"

**Causa:** AWS CLI no está instalado.

**Solución:**
```bash
# macOS
brew install awscli

# Configurar credenciales
aws configure
```

### Problema 3: "Error: No valid credential sources found"

**Causa:** AWS CLI no está configurado con credenciales.

**Solución:**
```bash
aws configure
# Ingresa:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output format: json
```

### Problema 4: Simulador no se conecta a IoT Core

**Síntomas:**
```
ERROR: Connection refused
ERROR: SSL/TLS handshake failed
```

**Soluciones:**
1. Verifica que el endpoint en `config.yaml` es correcto
2. Verifica que los certificados están en `simulator/certs/`
3. Verifica que el certificado está activo en la consola de AWS IoT
4. Verifica que la policy del certificado tiene permisos correctos

### Problema 5: API devuelve 401 Unauthorized

**Síntomas:**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing or invalid API key"
  }
}
```

**Soluciones:**
1. Verifica que estás enviando el header `x-api-key`
2. Verifica que el valor de API_KEY es correcto:
   ```bash
   cd terraform
   terraform output api_key
   ```
3. Verifica que la variable de entorno está configurada:
   ```bash
   echo $API_KEY
   ```

### Problema 6: Dashboard muestra "Failed to fetch"

**Síntomas:**
- Dashboard muestra error de conexión
- Consola del navegador muestra "Network Error"

**Soluciones:**
1. Verifica que el archivo `.env` en `dashboard/` tiene las variables correctas
2. Verifica que la API_URL es correcta:
   ```bash
   cat dashboard/.env
   ```
3. Reinicia el dashboard:
   ```bash
   # Presiona Ctrl+C para detener
   npm start
   ```
4. Verifica que la API está funcionando:
   ```bash
   curl -X GET "$API_URL/variables" -H "x-api-key: $API_KEY"
   ```

### Problema 7: No hay datos en DynamoDB

**Síntomas:**
```bash
aws dynamodb scan --table-name kia-paintshop-prototype-demo-sensor-data --limit 5
# Devuelve: "Count": 0
```

**Soluciones:**
1. Verifica que el simulador está corriendo y publicando mensajes
2. Verifica los logs de la Lambda de ingesta:
   ```bash
   aws logs tail /aws/lambda/kia-paintshop-ingest-demo --since 5m
   ```
3. Verifica que la IoT Rule está activa en la consola de AWS
4. Espera al menos 2 minutos después de iniciar el simulador

### Problema 8: Terraform destroy falla

**Síntomas:**
```
Error: Error deleting S3 bucket: BucketNotEmpty
Error: Error deleting DynamoDB table: ResourceInUseException
```

**Soluciones:**
1. Vaciar el bucket S3 manualmente:
   ```bash
   aws s3 rm s3://kia-paintshop-prototype-demo-data --recursive
   ```
2. Esperar a que las tablas de DynamoDB terminen de procesar:
   ```bash
   # Espera 2-3 minutos y vuelve a intentar
   terraform destroy -auto-approve
   ```
3. Si persiste, eliminar recursos manualmente desde la consola de AWS

### Problema 9: Costos más altos de lo esperado

**Síntomas:**
- Cost Explorer muestra costos > $10/semana
- Alarma de presupuesto se activa

**Soluciones:**
1. Verifica que el simulador no está corriendo 24/7
2. Verifica que no hay recursos duplicados:
   ```bash
   bash scripts/verify_cleanup.sh
   ```
3. Ejecuta teardown inmediatamente:
   ```bash
   bash scripts/teardown.sh
   ```
4. Revisa el desglose de costos en Cost Explorer para identificar el servicio costoso

### Problema 10: Dashboard no se actualiza automáticamente

**Síntomas:**
- Dashboard muestra datos pero no se actualiza cada 30 segundos
- Tienes que refrescar la página manualmente

**Soluciones:**
1. Verifica la consola del navegador (F12) para errores
2. Verifica que TanStack Query está configurado correctamente
3. Verifica que el simulador está corriendo y generando datos nuevos
4. Reinicia el dashboard:
   ```bash
   # Presiona Ctrl+C
   npm start
   ```

---

## 📝 Reporte Final

Después de completar todas las pruebas, prepara un reporte con esta estructura:

### 1. Resumen Ejecutivo
- Fecha de las pruebas
- Duración total de las pruebas
- Resultado general: ✅ Exitoso / ❌ Con problemas

### 2. Resultados por Fase

**Fase 1: Preparación del Entorno**
- ✅/❌ Estado
- Problemas encontrados (si los hubo)
- Tiempo invertido

**Fase 2: Despliegue de Infraestructura**
- ✅/❌ Estado
- Número de recursos creados
- Problemas encontrados
- Tiempo invertido

**Fase 3: Pruebas del Simulador**
- ✅/❌ Estado
- Número de variables simuladas
- Frecuencia de publicación
- Problemas encontrados
- Tiempo invertido

**Fase 4: Pruebas del Backend**
- ✅/❌ Estado
- Lambdas probadas (3/3)
- Alarmas generadas
- Problemas encontrados
- Tiempo invertido

**Fase 5: Pruebas de la API**
- ✅/❌ Estado
- Endpoints probados (5/5)
- Autenticación verificada
- Problemas encontrados
- Tiempo invertido

**Fase 6: Pruebas del Dashboard**
- ✅/❌ Estado
- Componentes verificados (5/5)
- Auto-refresh funcionando
- Problemas encontrados
- Tiempo invertido

**Fase 7: Verificación de Costos**
- ✅/❌ Estado
- Costo total de 7 días: $X.XX
- Costo proyectado de 30 días: $X.XX
- Dentro del presupuesto: ✅/❌
- Tiempo invertido

**Fase 8: Limpieza Final**
- ✅/❌ Estado
- Recursos eliminados correctamente
- Verificación de cleanup exitosa
- Tiempo invertido

### 3. Métricas del Sistema

**Infraestructura:**
- Recursos creados: 50+
- Tablas DynamoDB: 4
- Funciones Lambda: 8
- Endpoints API: 5

**Datos:**
- Variables monitoreadas: 97
- Frecuencia de muestreo: 30 segundos
- Puntos de datos generados: ~XXXX
- Alarmas generadas: XX

**Rendimiento:**
- Latencia promedio de API: XX ms
- Tiempo de respuesta del dashboard: XX ms
- Tasa de éxito de publicación MQTT: XX%

**Costos:**
- Costo total del proyecto: $X.XX
- Costo por día: $X.XX
- Costo proyectado mensual: $X.XX
- Porcentaje del presupuesto usado: X%

### 4. Capturas de Pantalla

Incluye capturas de pantalla de:
- [ ] Lista de variables en el dashboard
- [ ] Gráfico de una variable con datos
- [ ] Panel de alarmas
- [ ] Tarjeta de estadísticas
- [ ] Cost Explorer mostrando desglose de costos
- [ ] Consola de AWS mostrando recursos (DynamoDB, Lambda, IoT)
- [ ] Verificación de cleanup (sin recursos)

### 5. Problemas Encontrados y Soluciones

Para cada problema encontrado, documenta:
- **Descripción del problema:** ¿Qué falló?
- **Fase donde ocurrió:** ¿En qué fase?
- **Mensaje de error:** Copia el error exacto
- **Solución aplicada:** ¿Cómo lo resolviste?
- **Tiempo para resolver:** ¿Cuánto tardaste?

Ejemplo:
```
Problema: Simulador no se conectaba a IoT Core
Fase: Fase 3 - Pruebas del Simulador
Error: "SSL/TLS handshake failed"
Solución: Descargué nuevamente el certificado raíz de Amazon
Tiempo: 15 minutos
```

### 6. Lecciones Aprendidas

Reflexiona sobre:
- ¿Qué aprendiste sobre AWS?
- ¿Qué aprendiste sobre IoT?
- ¿Qué aprendiste sobre arquitecturas serverless?
- ¿Qué fue lo más difícil?
- ¿Qué fue lo más interesante?
- ¿Qué harías diferente la próxima vez?

### 7. Recomendaciones

Basándote en tu experiencia:
- ¿El sistema está listo para producción?
- ¿Qué mejoras sugerirías?
- ¿Hay algún riesgo que identificaste?
- ¿La documentación fue suficiente?
- ¿Qué documentación adicional sería útil?

### 8. Conclusión

Resume en 2-3 párrafos:
- Si el MVP cumple con los requisitos del proyecto
- Si el sistema está listo para ser presentado
- Tu nivel de confianza en el sistema (1-10)
- Próximos pasos recomendados

---

## 🎓 Recursos Adicionales para Aprender

### Documentación Oficial

**AWS:**
- AWS Getting Started: https://aws.amazon.com/getting-started/
- AWS IoT Core Documentation: https://docs.aws.amazon.com/iot/
- DynamoDB Documentation: https://docs.aws.amazon.com/dynamodb/
- Lambda Documentation: https://docs.aws.amazon.com/lambda/

**Terraform:**
- Terraform AWS Provider: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Terraform Tutorials: https://developer.hashicorp.com/terraform/tutorials

**React:**
- React Documentation: https://react.dev/
- TypeScript Handbook: https://www.typescriptlang.org/docs/

### Tutoriales Recomendados

**Para entender IoT:**
- "What is IoT?" - AWS IoT Core Tutorial
- "MQTT Protocol Explained" - HiveMQ Blog

**Para entender Serverless:**
- "AWS Lambda for Beginners" - AWS Training
- "Serverless Architecture Patterns" - AWS Whitepapers

**Para entender APIs REST:**
- "REST API Tutorial" - RESTfulAPI.net
- "HTTP Methods Explained" - MDN Web Docs

**Para entender Testing:**
- "Property-Based Testing with Hypothesis" - Hypothesis Documentation
- "Unit Testing Best Practices" - pytest Documentation

### Videos Recomendados (YouTube)

- "AWS IoT Core Tutorial" - AWS Online Tech Talks
- "Serverless Architecture Explained" - AWS re:Invent
- "DynamoDB Deep Dive" - AWS re:Invent
- "React Crash Course" - Traversy Media
- "Terraform Tutorial for Beginners" - TechWorld with Nana

### Libros Recomendados

- "AWS Certified Solutions Architect Study Guide" - Ben Piper
- "Serverless Architectures on AWS" - Peter Sbarski
- "Learning React" - Alex Banks & Eve Porcello
- "Terraform: Up & Running" - Yevgeniy Brikman

---

## 📞 Contacto y Soporte

Si encuentras problemas que no puedes resolver con esta guía:

1. **Revisa la documentación del proyecto:**
   - `README.md` - Overview general
   - `docs/TROUBLESHOOTING.md` - Guía de solución de problemas
   - `docs/API.md` - Documentación de la API
   - `docs/IOT_SETUP.md` - Configuración de IoT

2. **Revisa los logs:**
   - CloudWatch Logs para Lambdas
   - Consola del navegador para el dashboard
   - Output del simulador en la terminal

3. **Consulta con tu equipo:**
   - Comparte el mensaje de error exacto
   - Comparte los pasos que seguiste
   - Comparte las capturas de pantalla relevantes

4. **Recursos de la comunidad:**
   - AWS Forums: https://forums.aws.amazon.com/
   - Stack Overflow: https://stackoverflow.com/ (tag: aws, terraform, react)
   - Reddit: r/aws, r/terraform, r/reactjs

---

## 🎉 ¡Felicidades!

Si completaste todas las fases de esta guía, has logrado:

✅ Desplegar una arquitectura serverless completa en AWS  
✅ Configurar y ejecutar un simulador IoT con MQTT  
✅ Probar 8 funciones Lambda trabajando en conjunto  
✅ Validar una API REST con 5 endpoints  
✅ Verificar un dashboard web en tiempo real  
✅ Gestionar costos y presupuestos en AWS  
✅ Eliminar recursos de forma segura y completa  

**Esto es un logro significativo, especialmente para alguien en segundo semestre.**

Has demostrado que puedes:
- Trabajar con tecnologías cloud modernas
- Seguir documentación técnica compleja
- Resolver problemas de forma independiente
- Validar sistemas end-to-end
- Gestionar recursos y costos

**¡Sigue aprendiendo y construyendo cosas increíbles!** 🚀

---

**Versión:** 1.0  
**Última actualización:** 19 de febrero de 2026  
**Autor:** Equipo KIA Paint Shop IoT Prototype  
**Licencia:** Uso interno - KIA Motors
