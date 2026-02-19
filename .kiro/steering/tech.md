---
inclusion: always
---

# Technology Stack

## Backend

- Python 3.11 (all Lambda functions and simulator)
- boto3 >= 1.34.0 (AWS SDK)
- paho-mqtt (IoT device simulation)
- numpy (statistical calculations)
- PyYAML (configuration)

## Frontend

- React 18.2.0
- TypeScript 5.3.3
- TanStack Query 5.17.19 (data fetching/caching)
- Recharts 2.10.4 (visualization)
- Tailwind CSS 3.4.1 (styling)
- Axios 1.6.5 (HTTP client)

## Infrastructure

- Terraform >= 1.5.0 (Infrastructure as Code)
- AWS Services:
  - IoT Core (MQTT ingestion with X.509 auth)
  - Lambda (Python 3.11 runtime)
  - DynamoDB (on-demand billing)
  - S3 (Parquet archival)
  - API Gateway (REST API)
  - EventBridge (event orchestration)
  - CloudWatch (logging/monitoring)

## Testing

- pytest (unit tests)
- Hypothesis (property-based testing)
- moto (AWS service mocking)
- @testing-library/react (React component testing)

## Common Commands

### Infrastructure
```bash
# Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# Get outputs
terraform output -json > ../outputs.json

# Destroy everything
terraform destroy -auto-approve
```

### Simulator
```bash
# Install dependencies
pip install -r requirements.txt

# Run simulator
cd simulator
python simulator.py --config config.yaml
```

### Dashboard
```bash
cd dashboard

# Install dependencies
npm install

# Development server (manual - don't use in automation)
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run property-based tests only
pytest tests/property/ -v --hypothesis-show-statistics

# Run unit tests only
pytest tests/unit/ -v

# Run with coverage
pytest tests/ --cov=lambdas --cov=simulator
```

## Build System

- No build step for Python Lambda functions (deployed as source)
- React uses Create React App (react-scripts)
- Terraform manages all AWS resources
- No Docker containers (pure serverless)

## Configuration

- Environment variables via `.env` files (never commit)
- Terraform variables in `terraform/variables.tf`
- Simulator config in `simulator/config.yaml`
- Dashboard config via `REACT_APP_*` environment variables
