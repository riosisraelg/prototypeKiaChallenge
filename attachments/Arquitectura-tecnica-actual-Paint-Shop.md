Arquitectura técnica actual del Paint Shop: Descripción general de los sistemas, dispositivos y plataformas que hoy intervienen en el Paint Shop (sensores, PLCs, SCADA, MES, bases de datos, etc.), así como  qué tipo de datos generan  y  en qué formato , sin incluir información sensible.
Proceso Fisico (Paint Shop)
Considerar la siguiente estructura para la integración del proyecto:
Proceso → PLC → WinCC → Operador → WinCC → PLC → Proceso

PROCESO (Paint Shop)
• Sensores: Temp Horno, Presión Pintura, Posición carrier
• Actuadores: Motores, Quemadores, Bombas, Robots
      |
      v (señales físicas)
      |
PLC (Siemens S7300)
• Lógica de control, Secuencias, Interlocks, Seguridad
• Ejemplos de variables: Oven_Temp_Actual, Conveyor_Run, Booth1_Fault
      |
      v (PROFINET / tags)
      |
WinCC V7 (SIMATIC HMI)
• Pantallas, Alarmas, Tendencias, Usuarios
      |
      v (interacción)
      |
OPERADOR
• Ve estado del proceso, Reconoce alarmas, Ajusta setpoints, Arranca / Para línea

+---------------------------------------+
|                PROCESO                |
|             (Paint Shop)              |
|                                       |
| • Sensores                            |
|   - Temp Horno                        |
|   - Presión Pintura                   |
|   - Posición carrier                  |
|                                       |
| • Actuadores                          |
|   - Motores                           |
|   - Quemadores                        |
|   - Bombas                            |
|   - Robots                            |
+---------------------------------------+
                   ^
                   | señales físicas
                   v
+---------------------------------------+
|                  PLC                  |
|            (Siemens S7300)            |
|                                       |
| • Lógica de control                   |
| • Secuencias                          |
| • Interlocks                          |
| • Seguridad                           |
|                                       |
| Ejemplos de variables:                |
|   Oven_Temp_Actual                    |
|   Conveyor_Run                        |
|   Booth1_Fault                        |
+---------------------------------------+
                   ^
                   | PROFINET
                   | (tags)
                   v
+---------------------------------------+
|               WinCC V7                |
|             (SIMATIC HMI)             |
|                                       |
| • Pantallas                           |
| • Alarmas                             |
| • Tendencias                          |
| • Usuarios                            |
+---------------------------------------+
                   ^
                   | interacción
                   v
+---------------------------------------+
|               OPERADOR                |
| • Ve estado del proceso               |
| • Reconoce alarmas                    |
| • Ajusta setpoints                    |
| • Arranca / Para línea                |
+---------------------------------------+

Lineamientos de conectividad y comunicación entre dispositivos: Documento que indique  qué protocolos, estándares o tipos de comunicación  son viables (ej. OPC UA, MQTT, APIs, integraciones indirectas), así como  restricciones técnicas  a considerar para conectar nuevos dispositivos o sistemas.
Para el alcance del proyecto (digitalización del proceso de Pre-Tratamiento y E-Coat) la opción mas viable seria OPC UA para una primera fase, considerando tener un flujo directo de datos de PLC/equipo a SCADA.
En una siguiente fase la ideal sería usar MQTT para el análisis de datos.
Restricciones técnicas no evidentes en los videos: Lineamientos sobre limitaciones específicas que no son visibles para los estudiantes (compatibilidad tecnológica, ciberseguridad industrial, uso de cloud vs on-premise, certificaciones requeridas), para asegurar que las propuestas sean  realistas y viables .
Para el proyecto el uso de cloud no sería tan viable ya que en KMX existen restricciones sobre el procesamiento de datos en servidores externos, por lo que una propuesta on-premise seria lo más recomendable.
Ciberseguridad
Existen seis firewalls de seguridad perimetral que protegen la red de Kia Motors México.
Estos dispositivos bloquean la comunicación del exterior hacia el interior de la red, permitiendo únicamente la autorización de ciertos servicios mediante el uso de listas de control de acceso (ACL), utilizando una dirección IP y el puerto/protocolo que será usado por cada servicio, asegurando así un control total sobre quién y cómo acceden a la red de la compañía.
Se utilizan 4 sistemas IPS (Intrusion Protection System) para proteger la red contra ataques y accesos no autorizados.
Estos dispositivos analizan todo el tráfico que entra o sale de la red, detectando y bloqueando paquetes mediante perfiles de seguridad configurados.
El antivirus Symantec Endpoint Protection se utiliza para la protección de las computadoras de los usuarios.
Este sistema antivirus cuenta con protección contra virus, spyware, amenazas proactivas y amenazas de red.
El antivirus se actualiza constantemente cada 4 horas en toda la red.
Además, tiene programado un escaneo activo diario y un escaneo completo semanal del equipo, con instrucciones para eliminar o poner en cuarentena las amenazas detectadas.
El antivirus OfficeScan de TrendMicro se utiliza para proteger los servidores contra virus, malware, spyware y grayware, mediante un escaneo en tiempo real activo las 24 horas del día.