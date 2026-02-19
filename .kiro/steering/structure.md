---
inclusion: always
---

# Project Structure

## Directory Organization

```
.
├── terraform/              # Infrastructure as Code (12 files, ~88KB)
│   ├── main.tf            # Main configuration
│   ├── variables.tf       # Input variables
│   ├── outputs.tf         # Output values
│   ├── dynamodb.tf        # 4 DynamoDB tables
│   ├── iot.tf             # IoT Core setup
│   ├── s3.tf              # S3 bucket with lifecycle
│   ├── monitoring.tf      # CloudWatch + SNS
│   ├── lambda_*.tf        # Lambda function configs (4 files)
│   └── api_gateway.tf     # API Gateway with 5 endpoints
│
├── simulator/             # Python IoT data simulator
│   ├── simulator.py       # Main orchestrator
│   ├── config_loader.py   # CSV variable loader
│   ├── data_generator.py  # Realistic data generation
│   ├── mqtt_publisher.py  # MQTT/TLS publishing
│   ├── alarm_simulator.py # Alarm detection
│   ├── config.yaml        # Simulator configuration
│   └── certs/             # IoT X.509 certificates (gitignored)
│
├── lambdas/               # AWS Lambda functions
│   ├── ingest/            # IoT message ingestion
│   │   ├── handler.py     # Main handler
│   │   └── validators.py  # JSON schema validation
│   ├── process/           # Anomaly detection & alarms
│   │   ├── handler.py
│   │   └── anomaly_detector.py
│   ├── statistics/        # Statistical calculations
│   │   ├── handler.py
│   │   └── statistics_calculator.py
│   └── api/               # REST API handlers (5 endpoints)
│       ├── list_variables.py
│       ├── get_variable_data.py
│       ├── list_alarms.py
│       ├── acknowledge_alarm.py
│       ├── get_statistics.py
│       ├── auth_middleware.py    # API key auth
│       └── error_handler.py      # Error formatting
│
├── dashboard/             # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx        # Main layout
│   │   ├── components/    # React components (5 files)
│   │   ├── hooks/         # Custom hooks (useVariableData)
│   │   ├── services/      # API client (axios)
│   │   └── types/         # TypeScript definitions
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
│
├── tests/                 # Test suite (212+ tests)
│   ├── property/          # Property-based tests (Hypothesis)
│   │   ├── test_properties_data_generator.py
│   │   ├── test_properties_alarm_generation.py
│   │   ├── test_properties_storage.py
│   │   └── test_properties_api_roundtrip.py
│   └── unit/              # Unit tests
│       ├── test_alarm_simulator.py
│       ├── test_ingest_handler.py
│       ├── test_list_variables.py
│       └── test_get_variable_data.py
│
├── docs/                  # Additional documentation
│   ├── API.md
│   ├── VARIABLES.md
│   ├── COSTS.md
│   ├── IOT_SETUP.md
│   └── TROUBLESHOOTING.md
│
├── scripts/               # Management scripts
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
└── README.md              # Project overview
```

## Key Patterns

### Lambda Function Structure
Each Lambda has:
- `handler.py` - Main entry point with `lambda_handler(event, context)`
- `requirements.txt` - Dependencies (boto3 minimal)
- `README.md` - Documentation
- Separate business logic modules (validators, calculators, etc.)

### API Handlers
- One file per endpoint
- Shared utilities: `auth_middleware.py`, `error_handler.py`
- Consistent response format with CORS headers
- API key authentication on all endpoints

### Terraform Modules
- Modular structure: one file per AWS service category
- Variables in `variables.tf`, outputs in `outputs.tf`
- Resource naming: `{project_name}-{environment}-{resource}`
- Tags: Project, Environment on all resources

### Testing Structure
- Property-based tests validate invariants (Hypothesis)
- Unit tests validate specific behaviors (pytest)
- Test files mirror source structure
- Fixtures in conftest.py files

### Configuration Files
- `.env` - Local environment variables (gitignored)
- `config.yaml` - Simulator configuration
- `variables.tf` - Terraform variables
- `package.json` - Frontend dependencies

## Naming Conventions

- Python: snake_case for files, functions, variables
- TypeScript/React: PascalCase for components, camelCase for functions
- Terraform: snake_case for resources, kebab-case for names
- AWS Resources: `kia-paintshop-prototype-{env}-{resource}`
- Lambda Functions: `{project}-{function}-{env}`
- DynamoDB Tables: `{project}-{table}-{env}`

## Important Files

- `README.md` - Start here for project overview
- `DEPLOYMENT_INSTRUCTIONS.md` - Deployment guide
- `PROJECT_HEALTH_REPORT_FINAL.md` - Current project status
- `.env.example` - Required environment variables template
- `terraform/outputs.tf` - Critical outputs (API URL, IoT endpoint)
