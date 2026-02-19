# 🏭 KIA Paint Shop IoT Prototype

> Sistema serverless en AWS para monitorear 100 variables del proceso de pintura de KIA

[![Status](https://img.shields.io/badge/Status-Listo%20para%20Testing-success)](PROYECTO_LISTO_PARA_TESTING.md)
[![Cost](https://img.shields.io/badge/Costo-$1--5%2Fmes-green)](docs/COSTS.md)
[![MVP](https://img.shields.io/badge/MVP-100%25%20Completo-blue)](PROJECT_HEALTH_REPORT_FINAL.md)

---

## 🎯 ¿Qué es este proyecto?

Un prototipo que simula el monitoreo en tiempo real de 100 variables del proceso de pintura de KIA usando servicios de AWS IoT. El sistema:

- 📊 Monitorea 100 variables cada 30 segundos
- 🚨 Detecta anomalías y genera alarmas
- 📈 Calcula estadísticas en tiempo real
- 🖥️ Muestra todo en un dashboard web
- 💰 Cuesta menos de $5/mes
- 🔄 Se puede crear y destruir completamente

---

## 🚀 Para Empezar (Testing)

### Si eres la persona que va a probar el proyecto:

**👉 Empieza aquí: [GUIA_TESTING_PRINCIPIANTES.md](GUIA_TESTING_PRINCIPIANTES.md)**

Esta guía te llevará paso a paso por todo el proceso de validación (3-4 horas).

### Prerequisitos

- Cuenta de AWS con permisos de administrador
- AWS CLI instalado y configurado
- Terraform >= 1.5.0
- Python 3.11+
- Node.js 18+ y npm

---

## 📁 Estructura del Proyecto

```
.
├── GUIA_TESTING_PRINCIPIANTES.md  ← EMPIEZA AQUÍ
├── terraform/                      # Infraestructura (50+ recursos AWS)
├── simulator/                      # Simulador IoT (97 variables)
├── lambdas/                        # 8 funciones Lambda
├── dashboard/                      # Dashboard React + TypeScript
├── tests/                          # 212+ tests
├── scripts/                        # Scripts de gestión
└── docs/                           # Documentación adicional
```


---

## 📚 Documentación

### Para Testing
- **[GUIA_TESTING_PRINCIPIANTES.md](GUIA_TESTING_PRINCIPIANTES.md)** - Guía completa paso a paso (EMPIEZA AQUÍ)
- **[PROYECTO_LISTO_PARA_TESTING.md](PROYECTO_LISTO_PARA_TESTING.md)** - Validación técnica del proyecto
- **[RESUMEN_PARA_TI.md](RESUMEN_PARA_TI.md)** - Resumen ejecutivo

### Documentación Técnica
- **[README.md](README.md)** - Documentación técnica completa
- **[docs/API.md](docs/API.md)** - Documentación de la API REST
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Solución de problemas
- **[docs/COSTS.md](docs/COSTS.md)** - Análisis de costos
- **[docs/VARIABLES.md](docs/VARIABLES.md)** - Configuración de variables

### Reportes del Proyecto
- **[PROJECT_HEALTH_REPORT_FINAL.md](PROJECT_HEALTH_REPORT_FINAL.md)** - Estado del proyecto (9.8/10)
- **[DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)** - Guía de deployment

---

## 🏗️ Arquitectura Simplificada

```
Simulador (Python)
    ↓ MQTT/TLS
AWS IoT Core
    ↓
Lambda Ingesta → DynamoDB (datos)
    ↓
Lambda Procesamiento → DynamoDB (alarmas)
    ↓
Lambda Estadísticas → DynamoDB (stats)
    ↓
API Gateway (REST)
    ↓
Dashboard (React)
```

---

## 💰 Costos

- **Costo estimado:** $1-5 USD/mes
- **Presupuesto:** $50 USD/mes
- **Uso del presupuesto:** 2-10%
- **Dentro del Free Tier de AWS:** ✅

Ver [docs/COSTS.md](docs/COSTS.md) para detalles.

---

## 🔒 Seguridad

- ✅ Autenticación con API key
- ✅ Certificados X.509 para IoT
- ✅ Encryption at rest (DynamoDB, S3)
- ✅ TLS 1.2+ en todas las comunicaciones
- ✅ IAM roles con mínimo privilegio

Ver [docs/SECURITY.md](docs/SECURITY.md) para detalles.

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa [GUIA_TESTING_PRINCIPIANTES.md](GUIA_TESTING_PRINCIPIANTES.md) - Sección "Solución de Problemas"
2. Revisa [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. Contacta al equipo

---

## 📄 Licencia

Uso interno - KIA Motors

---

**Versión:** 1.0  
**Última actualización:** 19 de febrero de 2026  
**Estado:** ✅ Listo para Testing
