# KIA Paint Shop IoT Prototype - Project Structure

Estructura organizada del proyecto después de la reorganización.

## 📁 Estructura de Directorios

```
kia-paint-shop-iot-prototype/
│
├── 📂 terraform/              # Infrastructure as Code (12 files, ~88KB)
│   ├── main.tf               # Main Terraform configuration
│   ├── variables.tf          # Input variables
│   ├── outputs.tf            # Output values
│   ├── dynamodb.tf           # 4 DynamoDB tables
│   ├── iot.tf                # IoT Core setup
│   ├── s3.tf                 # S3 bucket with lifecycle
│   ├── monitoring.tf         # CloudWatch + SNS
│   ├── lambda_ingest.tf      # Ingest Lambda config
│   ├── lambda_process.tf     # Process Lambda config
│   ├── lambda_statistics.tf  # Statistics Lambda config
│   ├── lambda_api.tf         # 5 API Lambda configs
│   ├── api_gateway.tf        # API Gateway with 5 endpoints
│   └── kia-iot-policy.json   # IoT policy document
│
├── 📂 simulator/              # Python IoT data simulator
│   ├── simulator.py          # Main orchestrator
│   ├── config_loader.py      # CSV variable loader (97 vars)
│   ├── data_generator.py     # Realistic data generation
│   ├── mqtt_publisher.py     # MQTT/TLS publishing
│   ├── alarm_simulator.py    # Alarm detection
│   ├── config.yaml           # Simulator configuration
│   ├── certs/                # IoT X.509 certificates (gitignored)
│   └── README.md             # Simulator documentation
│
├── 📂 lambdas/                # AWS Lambda functions
│   ├── ingest/               # IoT message ingestion
│   │   ├── handler.py        # Main handler
│   │   ├── validators.py     # JSON schema validation
│   │   └── README.md
│   ├── process/              # Anomaly detection & alarms
│   │   ├── handler.py
│   │   ├── anomaly_detector.py
│   │   └── README.md
│   ├── statistics/           # Statistical calculations
│   │   ├── handler.py
│   │   ├── statistics_calculator.py
│   │   ├── requirements.txt  # numpy dependency
│   │   └── README.md
│   ├── api/                  # REST API handlers (5 endpoints)
│   │   ├── list_variables.py
│   │   ├── get_variable_data.py
│   │   ├── list_alarms.py
│   │   ├── acknowledge_alarm.py
│   │   ├── get_statistics.py
│   │   ├── auth_middleware.py    # API key auth
│   │   ├── error_handler.py      # Error formatting
│   │   └── README.md
│   └── common/               # Shared utilities
│       └── logger.py         # Structured logging
│
├── 📂 dashboard/              # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx           # Main layout
│   │   ├── components/       # React components
│   │   │   ├── VariableList.tsx
│   │   │   ├── VariableChart.tsx
│   │   │   ├── AlarmPanel.tsx
│   │   │   ├── StatisticsCard.tsx
│   │   │   └── ConnectionStatus.tsx
│   │   ├── hooks/            # Custom hooks
│   │   │   └── useVariableData.ts
│   │   ├── services/         # API client (axios)
│   │   │   └── api.ts
│   │   └── types/            # TypeScript definitions
│   │       └── index.ts
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
├── 📂 tests/                  # Test suite (212+ tests)
│   ├── property/             # Property-based tests (Hypothesis)
│   │   ├── test_properties_config_loader.py
│   │   ├── test_properties_data_generator.py
│   │   ├── test_properties_alarm_generation.py
│   │   ├── test_properties_mqtt_topics.py
│   │   ├── test_properties_json_validation.py
│   │   ├── test_properties_storage.py
│   │   ├── test_properties_alarm_persistence.py
│   │   ├── test_properties_statistics.py
│   │   ├── test_properties_api_roundtrip.py
│   │   ├── test_properties_x509_auth.py
│   │   ├── test_properties_logging.py
│   │   └── test_properties_metrics.py
│   └── unit/                 # Unit tests
│       ├── test_alarm_simulator.py
│       ├── test_ingest_handler.py
│       ├── test_anomaly_detector.py
│       ├── test_process_handler.py
│       ├── test_list_variables.py
│       ├── test_get_variable_data.py
│       ├── test_list_alarms.py
│       ├── test_acknowledge_alarm.py
│       └── test_get_statistics.py
│
├── 📂 scripts/                # Management scripts
│   ├── setup.sh              # Complete deployment automation
│   ├── teardown.sh           # Safe resource destruction
│   ├── check_costs.sh        # Cost monitoring
│   ├── verify_cleanup.sh     # Cleanup verification
│   ├── verify_security.sh    # Security verification
│   ├── analyze_csvs.py       # CSV analysis tool
│   ├── check_data.py         # Data validation
│   ├── generate_report.py    # Report generation
│   ├── create_final_report.py # Final report creation
│   └── README.md
│
├── 📂 docs/                   # Technical documentation
│   ├── API.md                # REST API reference
│   ├── VARIABLES.md          # Variable configuration guide
│   ├── COSTS.md              # Cost analysis and optimization
│   ├── SECURITY.md           # Security configuration
│   ├── IAM_PERMISSIONS.md    # IAM roles documentation
│   ├── TROUBLESHOOTING.md    # Common issues and solutions
│   └── IOT_SETUP.md          # IoT Core setup guide
│
├── 📂 project-docs/           # Project documentation
│   ├── README.md             # Index of project docs
│   ├── GUIA_TESTING_PRINCIPIANTES.md  # Testing guide (Spanish)
│   ├── DEPLOYMENT_INSTRUCTIONS.md     # Detailed deployment guide
│   ├── VALIDATION_INSTRUCTIONS.md     # Validation procedures
│   ├── DASHBOARD_VERIFICATION_GUIDE.md # Dashboard testing
│   ├── PROYECTO_LISTO_PARA_TESTING.md # Project readiness (Spanish)
│   ├── README_SIMPLE.md               # Beginner-friendly overview
│   ├── RESUMEN_PARA_TI.md             # Summary for testers (Spanish)
│   ├── INSTRUCCIONES_FINALES_PARA_TI.md # Final instructions (Spanish)
│   ├── GIT_SETUP_COMPLETO.md          # Git setup guide (Spanish)
│   └── FINAL_VALIDATION_GUIDE.md      # Final validation steps
│
├── 📂 reports/                # Project reports and analysis
│   ├── README.md             # Index of reports
│   ├── PROJECT_HEALTH_REPORT_FINAL.md # Project status (9.8/10)
│   ├── PROJECT_HEALTH_REPORT.md       # Previous health report
│   ├── IAM_SECURITY_AUDIT.md          # Security audit results
│   ├── CHECKPOINT_5_SUMMARY.md        # Checkpoint summaries
│   ├── CHECKPOINT_9_VERIFICATION.md
│   ├── TASK_10_COMPLETION_SUMMARY.md  # Task summaries
│   ├── TASK_20_EXECUTIVE_SUMMARY.md
│   ├── analysis_report.md             # Variable analysis
│   ├── NEW_CHAT_SUMMARY.md            # Session summaries
│   ├── session1ResolucionDeDudas.md
│   ├── variableAnalisys-by-Amazon-Q.md
│   └── posiblePlanTrabajo-SketchedByAmazonQ.md
│
├── 📂 attachments/            # Project attachments and references
│   ├── README.md             # Index of attachments
│   ├── Paint-LAY-OUT.pdf     # Paint shop layout
│   ├── KMX-PA-PT-F-001.csv   # Pre-Treatment variables (48)
│   ├── KMX-PA-PE-F-001.csv   # E-Coat variables (18)
│   ├── KMX-PA-PE-F-001-Reporte-diario-laboratorio-ED.xlsx
│   ├── Ejemplo-Template-KIA-VF_IMU26.pptx
│   ├── Arquitectura-tecnica-actual-Paint-Shop.md
│   ├── Hoja-definicion-inicial-reto.md
│   ├── Guiones-Videos-Reto-KIA.md
│   └── Rubrica-evaluacion.md
│
├── 📂 .kiro/                  # Kiro configuration
│   ├── specs/                # Spec files
│   │   └── kia-paint-shop-iot-prototype/
│   │       ├── requirements.md
│   │       ├── design.md
│   │       └── tasks.md
│   └── steering/             # Steering rules
│       ├── product.md        # Product overview
│       ├── structure.md      # Project structure
│       └── tech.md           # Technology stack
│
├── 📄 .env.example            # Environment template
├── 📄 .gitignore              # Git ignore rules
├── 📄 requirements.txt        # Python dependencies
├── 📄 pytest.ini              # Pytest configuration
├── 📄 README.md               # Main project README
└── 📄 PROJECT_STRUCTURE.md    # This file

```

## 🗂️ Organización por Propósito

### 🔧 Código Fuente
- `terraform/` - Infrastructure as Code
- `simulator/` - IoT data simulator
- `lambdas/` - AWS Lambda functions
- `dashboard/` - React frontend

### 🧪 Testing
- `tests/property/` - Property-based tests (Hypothesis)
- `tests/unit/` - Unit tests (pytest)

### 📚 Documentación
- `docs/` - Documentación técnica (API, variables, costos, seguridad)
- `project-docs/` - Documentación del proyecto (guías, instrucciones)
- `reports/` - Reportes y análisis del proyecto
- `attachments/` - Archivos adjuntos y referencias

### 🛠️ Utilidades
- `scripts/` - Scripts de management y automatización
- `.kiro/` - Configuración de Kiro (specs, steering)

## 📊 Estadísticas del Proyecto

### Código
- **Terraform**: 12 archivos (~88KB)
- **Python**: 5 módulos del simulador + 8 Lambda functions
- **TypeScript/React**: 5 componentes + hooks + services
- **Tests**: 212+ tests (property-based + unit)

### Documentación
- **Technical Docs**: 7 archivos en `/docs`
- **Project Docs**: 10 archivos en `/project-docs`
- **Reports**: 12 archivos en `/reports`
- **Attachments**: 9 archivos en `/attachments`

### Variables Monitoreadas
- **Pre-Treatment (PT)**: 48 variables
- **E-Coat (ED)**: 18 variables
- **Production Control**: 34 variables
- **Total**: 100 variables

## 🔗 Navegación Rápida

### Para Empezar
1. **[README.md](README.md)** - Overview del proyecto
2. **[project-docs/README_SIMPLE.md](project-docs/README_SIMPLE.md)** - Introducción simplificada

### Para Testing
1. **[project-docs/GUIA_TESTING_PRINCIPIANTES.md](project-docs/GUIA_TESTING_PRINCIPIANTES.md)** - Guía completa
2. **[project-docs/PROYECTO_LISTO_PARA_TESTING.md](project-docs/PROYECTO_LISTO_PARA_TESTING.md)** - Validación

### Para Deployment
1. **[project-docs/DEPLOYMENT_INSTRUCTIONS.md](project-docs/DEPLOYMENT_INSTRUCTIONS.md)** - Instrucciones
2. **[docs/IOT_SETUP.md](docs/IOT_SETUP.md)** - Setup de IoT Core

### Para Entender el Proyecto
1. **[reports/PROJECT_HEALTH_REPORT_FINAL.md](reports/PROJECT_HEALTH_REPORT_FINAL.md)** - Estado actual
2. **[docs/VARIABLES.md](docs/VARIABLES.md)** - Variables monitoreadas
3. **[docs/COSTS.md](docs/COSTS.md)** - Análisis de costos

## 📝 Notas Importantes

### Archivos Trackeados en Git
Todos los archivos en `attachments/` están trackeados en Git (PDF, XLSX, PPTX, CSV, MD) ya que son parte integral del proyecto.

### Archivos Ignorados
- Certificados IoT (`simulator/certs/`)
- Environment variables (`.env`)
- Node modules (`node_modules/`)
- Python cache (`__pycache__/`)
- Terraform state (`*.tfstate`)
- Build artifacts (`dashboard/build/`)

### Estructura Limpia
La reorganización mantiene:
- ✅ Separación clara entre código y documentación
- ✅ Documentación organizada por propósito
- ✅ Attachments del proyecto accesibles
- ✅ Reportes y análisis centralizados
- ✅ Navegación intuitiva con READMEs en cada carpeta
