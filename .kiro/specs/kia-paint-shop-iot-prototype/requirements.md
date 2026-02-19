# Requerimientos Funcionales: Prototipo IoT Paint Shop KIA

## Contexto del Proyecto

Este es un **prototipo acelerado para demostración**, NO un sistema de producción. El objetivo es demostrar capacidades de digitalización en AWS al equipo de KIA, con las siguientes restricciones críticas:

- **Presupuesto**: <$50/mes (el usuario paga personalmente)
- **Escala**: ~100 variables (no las 130 del sistema completo)
- **Infraestructura efímera**: debe poder eliminarse completamente sin cargos residuales
- **Duración**: prototipo temporal para demostración

### Variables a Digitalizar

- **Pre-Treatment (PT)**: 48 variables del archivo KMX-PA-PT-F-001.csv
- **E-Coat (ED)**: 18 variables del archivo KMX-PA-PE-F-001.csv
- **Production Control**: 34 variables adicionales
- **Total**: ~100 variables para el prototipo

---

## Requerimiento 1: Simulación de Datos de Proceso

**User Story**: Como desarrollador del prototipo, necesito simular datos realistas de las 100 variables del paint shop, para poder demostrar el sistema sin acceso a equipos reales.

### Acceptance Criteria

1. WHEN el simulador inicia THEN el sistema SHALL cargar las definiciones de las 100 variables desde archivos de configuración basados en los CSVs reales (KMX-PA-PT-F-001.csv y KMX-PA-PE-F-001.csv)

2. WHEN el simulador genera datos THEN el sistema SHALL producir valores dentro de los rangos especificados para cada variable (min, max, unidades)

3. WHEN el simulador está en ejecución THEN el sistema SHALL generar datos a intervalos configurables (por defecto: cada 30 segundos)

4. WHEN el simulador genera datos THEN el sistema SHALL incluir timestamps precisos en formato ISO 8601 con zona horaria

5. WHEN el simulador detecta que una variable excede umbrales configurados THEN el sistema SHALL generar eventos de alarma con severidad apropiada

6. WHEN el simulador se detiene THEN el sistema SHALL cerrar conexiones limpiamente y registrar el evento de parada

---

## Requerimiento 2: Ingesta de Datos IoT

**User Story**: Como arquitecto del sistema, necesito ingestar datos de las variables del paint shop a través de AWS IoT Core, para centralizar la recolección de datos de manera escalable y segura.

### Acceptance Criteria

1. WHEN el simulador publica datos THEN el sistema SHALL enviar mensajes MQTT a AWS IoT Core usando certificados X.509 para autenticación

2. WHEN se publican datos THEN el sistema SHALL usar topics MQTT con estructura jerárquica: `kia/paintshop/{area}/{variable_id}`

3. WHEN IoT Core recibe mensajes THEN el sistema SHALL validar el formato JSON del payload antes de procesarlo

4. WHEN la conexión MQTT se interrumpe THEN el sistema SHALL reintentar automáticamente con backoff exponencial

5. WHEN el volumen de mensajes excede 400K/mes THEN el sistema SHALL registrar una advertencia (límite de capa gratuita: 500K/mes)

---

## Requerimiento 3: Almacenamiento de Datos

**User Story**: Como analista de datos, necesito almacenar los datos históricos de las variables, para poder consultar tendencias y generar reportes.

### Acceptance Criteria

1. WHEN IoT Core recibe datos THEN el sistema SHALL almacenar los datos en DynamoDB con TTL de 30 días para contener costos

2. WHEN se almacenan datos THEN el sistema SHALL usar una partition key compuesta por `{area}#{variable_id}` y sort key con timestamp

3. WHEN se consultan datos THEN el sistema SHALL permitir queries por rango de tiempo para una variable específica

4. WHEN el almacenamiento en DynamoDB excede 20GB THEN el sistema SHALL archivar datos antiguos a S3 en formato Parquet comprimido

5. WHEN se archivan datos a S3 THEN el sistema SHALL usar lifecycle policies para eliminar archivos después de 90 días

6. WHEN se eliminan datos THEN el sistema SHALL mantener integridad referencial y registrar la operación de eliminación

---

## Requerimiento 4: Procesamiento de Datos en Tiempo Real

**User Story**: Como ingeniero de proceso, necesito detectar anomalías y calcular estadísticas en tiempo real, para identificar problemas operacionales rápidamente.

### Acceptance Criteria

1. WHEN llegan datos nuevos THEN el sistema SHALL calcular estadísticas de ventana deslizante (promedio, min, max) para los últimos 10 minutos

2. WHEN una variable excede umbrales definidos THEN el sistema SHALL generar una alarma con nivel de severidad (warning, critical)

3. WHEN se genera una alarma THEN el sistema SHALL almacenarla en DynamoDB con estado (active, acknowledged, resolved)

4. WHEN se detectan patrones anómalos THEN el sistema SHALL registrar el evento con contexto (valores previos, timestamp, variable afectada)

5. WHEN el procesamiento falla THEN el sistema SHALL reintentar hasta 3 veces antes de enviar el mensaje a una cola de dead-letter

---

## Requerimiento 5: API REST para Consultas

**User Story**: Como desarrollador del dashboard, necesito una API REST para consultar datos y alarmas, para construir visualizaciones interactivas.

### Acceptance Criteria

1. WHEN se solicita GET /variables THEN el sistema SHALL retornar la lista de las 100 variables con sus metadatos (nombre, unidad, área, rangos)

2. WHEN se solicita GET /variables/{id}/data?start={ts}&end={ts} THEN el sistema SHALL retornar los datos históricos en el rango especificado

3. WHEN se solicita GET /alarms?status={status} THEN el sistema SHALL retornar alarmas filtradas por estado (active, acknowledged, resolved)

4. WHEN se solicita POST /alarms/{id}/acknowledge THEN el sistema SHALL actualizar el estado de la alarma a acknowledged

5. WHEN se solicita GET /statistics/{variable_id} THEN el sistema SHALL retornar estadísticas agregadas (promedio, min, max, desviación estándar) para las últimas 24 horas

6. WHEN la API recibe requests THEN el sistema SHALL validar autenticación usando API keys

7. WHEN la API retorna errores THEN el sistema SHALL usar códigos HTTP estándar y mensajes descriptivos en español

---

## Requerimiento 6: Dashboard Web

**User Story**: Como operador del paint shop, necesito un dashboard web para visualizar datos en tiempo real y gestionar alarmas, para monitorear el proceso de manera efectiva.

### Acceptance Criteria

1. WHEN el usuario accede al dashboard THEN el sistema SHALL mostrar las 100 variables organizadas por área (Pre-Treatment, E-Coat, Production Control)

2. WHEN se selecciona una variable THEN el sistema SHALL mostrar un gráfico de línea con los últimos 60 minutos de datos

3. WHEN hay alarmas activas THEN el sistema SHALL mostrar un panel de alarmas con indicadores visuales de severidad

4. WHEN el usuario hace clic en una alarma THEN el sistema SHALL permitir marcarla como acknowledged

5. WHEN se actualizan datos THEN el sistema SHALL refrescar automáticamente las visualizaciones cada 30 segundos

6. WHEN el dashboard se carga THEN el sistema SHALL mostrar indicadores de estado de conexión (conectado, desconectado, error)

---

## Requerimiento 7: Gestión de Costos y Recursos

**User Story**: Como administrador del prototipo, necesito controlar y monitorear los costos de AWS, para mantenerme dentro del presupuesto de $50/mes.

### Acceptance Criteria

1. WHEN se despliega la infraestructura THEN el sistema SHALL usar solo servicios con capa gratuita o costos mínimos (IoT Core, DynamoDB, Lambda, S3, API Gateway, Amplify)

2. WHEN se configuran servicios THEN el sistema SHALL establecer límites de uso: DynamoDB (25GB), IoT Core (500K mensajes/mes), Lambda (1M invocaciones/mes)

3. WHEN el uso se acerca a los límites THEN el sistema SHALL enviar notificaciones de advertencia via CloudWatch Alarms

4. WHEN se solicita estimación de costos THEN el sistema SHALL proporcionar un desglose mensual detallado por servicio

5. WHEN se ejecuta el script de teardown THEN el sistema SHALL eliminar todos los recursos de AWS sin dejar cargos residuales

6. WHEN se eliminan recursos THEN el sistema SHALL verificar que no queden recursos huérfanos (buckets S3, logs de CloudWatch, certificados IoT)

---

## Requerimiento 8: Infraestructura como Código

**User Story**: Como DevOps engineer, necesito gestionar toda la infraestructura con Terraform, para poder crear, modificar y destruir el entorno de manera reproducible.

### Acceptance Criteria

1. WHEN se ejecuta terraform apply THEN el sistema SHALL crear todos los recursos de AWS necesarios (IoT Core, DynamoDB, Lambda, API Gateway, S3, Amplify)

2. WHEN se configura Terraform THEN el sistema SHALL usar variables para parámetros configurables (región, nombres de recursos, límites)

3. WHEN se ejecuta terraform destroy THEN el sistema SHALL eliminar todos los recursos creados sin errores

4. WHEN se crean recursos THEN el sistema SHALL aplicar tags consistentes para identificación y gestión de costos (Project: KIA-PaintShop-Prototype, Environment: Demo)

5. WHEN se despliegan Lambdas THEN el sistema SHALL empaquetar el código Python con dependencias en archivos ZIP

6. WHEN se configura IoT Core THEN el sistema SHALL crear policies y certificados necesarios para autenticación MQTT

---

## Requerimiento 9: Monitoreo y Observabilidad

**User Story**: Como administrador del sistema, necesito monitorear la salud y rendimiento del prototipo, para detectar y resolver problemas rápidamente.

### Acceptance Criteria

1. WHEN los servicios están en ejecución THEN el sistema SHALL enviar métricas a CloudWatch (mensajes procesados, errores, latencia)

2. WHEN ocurren errores THEN el sistema SHALL registrar logs estructurados en CloudWatch Logs con nivel apropiado (INFO, WARNING, ERROR)

3. WHEN se configuran alarmas THEN el sistema SHALL crear CloudWatch Alarms para condiciones críticas (tasa de errores >5%, latencia >2s)

4. WHEN se dispara una alarma THEN el sistema SHALL enviar notificaciones via SNS (opcional, para contener costos)

5. WHEN se consultan logs THEN el sistema SHALL retener logs por 7 días para análisis (balance entre observabilidad y costos)

---

## Requerimiento 10: Seguridad y Autenticación

**User Story**: Como security engineer, necesito asegurar el acceso a los recursos del prototipo, para proteger los datos y prevenir accesos no autorizados.

### Acceptance Criteria

1. WHEN se conectan dispositivos IoT THEN el sistema SHALL requerir autenticación mediante certificados X.509

2. WHEN se accede a la API THEN el sistema SHALL validar API keys en headers de requests

3. WHEN se configuran permisos THEN el sistema SHALL usar IAM roles con principio de mínimo privilegio

4. WHEN se almacenan datos sensibles THEN el sistema SHALL usar encryption at rest en DynamoDB y S3

5. WHEN se transmiten datos THEN el sistema SHALL usar TLS 1.2+ para todas las comunicaciones

6. WHEN se crean recursos THEN el sistema SHALL deshabilitar acceso público por defecto (buckets S3, APIs)

---

## Restricciones Técnicas

### Servicios Prohibidos (por costo)
- AWS IoT SiteWise
- Amazon QuickSight
- Amazon Timestream
- SageMaker training jobs largos
- RDS/Aurora

### Servicios Permitidos (capa gratuita/bajo costo)
- AWS IoT Core (500K mensajes/mes gratis)
- DynamoDB (25GB gratis)
- Lambda (1M invocaciones/mes gratis)
- S3 (5GB gratis)
- API Gateway (1M requests/mes gratis)
- AWS Amplify (hosting gratis para apps pequeñas)
- CloudWatch (métricas básicas gratis)

### Límites de Escala
- Máximo 100 variables simultáneas
- Frecuencia de muestreo: 30 segundos (no tiempo real extremo)
- Retención de datos: 30 días en DynamoDB, 90 días en S3
- Usuarios concurrentes del dashboard: <10

---

## Criterios de Éxito del Prototipo

1. Demostrar ingesta de datos de 100 variables en tiempo real
2. Visualizar datos históricos y en tiempo real en dashboard web
3. Detectar y mostrar alarmas basadas en umbrales
4. Mantener costos mensuales <$50
5. Poder eliminar completamente la infraestructura en <5 minutos
6. Documentación clara para setup y teardown
