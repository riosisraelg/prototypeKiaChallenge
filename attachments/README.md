# Project Attachments

Esta carpeta contiene todos los archivos adjuntos y referencias del proyecto KIA Paint Shop.

## 📐 Planos y Layouts

- **[Paint-LAY-OUT.pdf](Paint-LAY-OUT.pdf)** - Layout del Paint Shop de KIA
  - Distribución física de la planta
  - Ubicación de sensores y equipos
  - Áreas: Pre-Treatment, E-Coat, Production Control

## 📊 Datos de Variables

### Pre-Treatment (PT)
- **[KMX-PA-PT-F-001.csv](KMX-PA-PT-F-001.csv)** - 48 variables de Pre-Tratamiento
  - Temperatura de tanques
  - pH de soluciones
  - Concentración de químicos
  - Flujo y presión

### E-Coat (ED)
- **[KMX-PA-PE-F-001.csv](KMX-PA-PE-F-001.csv)** - 18 variables de E-Coat
  - Voltaje y corriente
  - Temperatura de baño
  - Espesor de capa
  - Conductividad

- **[KMX-PA-PE-F-001-Reporte-diario-laboratorio-ED.xlsx](KMX-PA-PE-F-001-Reporte-diario-laboratorio-ED.xlsx)** - Reporte diario del laboratorio E-Coat
  - Datos históricos
  - Análisis de calidad
  - Métricas de producción

## 📋 Templates y Presentaciones

- **[Ejemplo-Template-KIA-VF_IMU26.pptx](Ejemplo-Template-KIA-VF_IMU26.pptx)** - Template de presentación KIA
  - Formato oficial
  - Branding KIA
  - Estructura de reportes

## 📄 Documentación del Reto

- **[Hoja-definicion-inicial-reto.md](Hoja-definicion-inicial-reto.md)** - Definición inicial del reto
  - Objetivos del proyecto
  - Alcance y limitaciones
  - Criterios de éxito

- **[Arquitectura-tecnica-actual-Paint-Shop.md](Arquitectura-tecnica-actual-Paint-Shop.md)** - Arquitectura técnica actual
  - Sistema legacy
  - Infraestructura existente
  - Puntos de integración

- **[Guiones-Videos-Reto-KIA.md](Guiones-Videos-Reto-KIA.md)** - Guiones para videos del reto
  - Scripts de presentación
  - Demos planificadas
  - Contenido de videos

- **[Rubrica-evaluacion.md](Rubrica-evaluacion.md)** - Rúbrica de evaluación
  - Criterios de evaluación
  - Puntajes y métricas
  - Requisitos de entrega

## 📊 Resumen de Variables

| Área | Variables | Archivo |
|------|-----------|---------|
| **Pre-Treatment (PT)** | 48 | KMX-PA-PT-F-001.csv |
| **E-Coat (ED)** | 18 | KMX-PA-PE-F-001.csv |
| **Production Control** | 34 | (Generadas por simulador) |
| **Total** | **100** | - |

## 🔍 Tipos de Variables Monitoreadas

### Pre-Treatment
- Temperatura (°C)
- pH
- Concentración (g/L)
- Flujo (L/min)
- Presión (bar)

### E-Coat
- Voltaje (V)
- Corriente (A)
- Temperatura (°C)
- Espesor (μm)
- Conductividad (μS/cm)

### Production Control
- Velocidad de línea (m/min)
- Tiempo de ciclo (s)
- Métricas de calidad
- Consumo energético (kWh)

## ⚠️ Importante

Estos archivos son parte integral del proyecto y **NO deben ser ignorados** por Git. El `.gitignore` está configurado para incluirlos explícitamente:

```gitignore
# IMPORTANT: Do NOT ignore project attachments
!*.pdf
!*.xlsx
!*.pptx
!*.csv
!*.md
```

## 🔗 Enlaces Relacionados

- **Documentación del Proyecto**: Ver carpeta `/project-docs`
- **Documentación Técnica**: Ver carpeta `/docs`
- **Reportes**: Ver carpeta `/reports`
- **README Principal**: Ver `/README.md`
- **Guía de Variables**: Ver `/docs/VARIABLES.md`
