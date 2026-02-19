# Management Scripts

This directory contains automation scripts for deploying, managing, and tearing down the KIA Paint Shop IoT Prototype.

## Available Scripts

### 1. setup.sh - Complete Deployment Automation

Automates the entire deployment process from infrastructure to configuration.

**Usage:**
```bash
./scripts/setup.sh
```

**What it does:**
1. Checks prerequisites (Terraform, AWS CLI, Python)
2. Verifies AWS credentials
3. Initializes and applies Terraform configuration
4. Retrieves deployment outputs (API URL, API Key, IoT endpoint)
5. Saves outputs to `.deployment_outputs` file
6. Tests API endpoints
7. Displays next steps for simulator and dashboard setup

**Prerequisites:**
- Terraform >= 1.5.0
- AWS CLI configured with credentials
- Python 3.11+
- Active AWS account

**Estimated Time:** 5-10 minutes

---

### 2. teardown.sh - Safe Resource Destruction

Safely destroys all AWS resources and cleans up local artifacts.

**Usage:**
```bash
./scripts/teardown.sh
```

**What it does:**
1. Confirms destruction with double-check prompts
2. Stops any running simulator processes
3. Empties S3 buckets (required before deletion)
4. Destroys all Terraform-managed resources
5. Cleans up local deployment files
6. Optionally removes IoT certificates
7. Runs cleanup verification

**Safety Features:**
- Requires typing "yes" to confirm
- Requires typing project name to double-confirm
- Empties S3 buckets before deletion
- Verifies cleanup after completion

**Estimated Time:** 3-5 minutes

---

### 3. check_costs.sh - Cost Monitoring

Monitors AWS costs and compares against the $50/month budget.

**Usage:**
```bash
./scripts/check_costs.sh
```

**What it displays:**
1. Total cost for current month (MTD)
2. Budget usage percentage
3. Cost breakdown by AWS service
4. Monthly cost projection
5. Resource usage estimates
6. Cost optimization tips

**Features:**
- Color-coded warnings (green/yellow/red)
- Budget threshold alerts (80% warning)
- Service-level cost breakdown
- Projected monthly costs
- Free tier usage tracking

**Requirements:**
- AWS Cost Explorer API access
- Python 3 (for calculations)
- bc (basic calculator)

**Estimated Time:** 30 seconds

---

### 4. verify_cleanup.sh - Cleanup Verification

Verifies that all AWS resources have been properly deleted after teardown.

**Usage:**
```bash
./scripts/verify_cleanup.sh
```

**What it checks:**
1. S3 buckets with project prefix
2. DynamoDB tables
3. Lambda functions
4. IoT Things and certificates
5. CloudWatch Log Groups
6. API Gateways
7. EventBridge Rules
8. IAM Roles
9. SNS Topics
10. SQS Queues

**Exit Codes:**
- `0` - All resources cleaned up successfully
- `1` - Found remaining resources (lists them)

**Estimated Time:** 30 seconds

---

### 5. verify_security.sh - Security Configuration Verification

Verifies that all security configurations are properly applied.

**Usage:**
```bash
./scripts/verify_security.sh
```

**What it checks:**
1. S3 bucket public access block (all 4 settings)
2. S3 bucket encryption (AES256)
3. DynamoDB table encryption (all tables)
4. IoT Core TLS configuration
5. API Gateway security settings
6. IAM role permissions (no wildcards)
7. Certificate file permissions (600)
8. No public Lambda URLs
9. No public resources exposed

**Security Checklist:**
- ✓ Encryption at rest (DynamoDB, S3)
- ✓ Encryption in transit (TLS 1.2+)
- ✓ X.509 authentication for IoT
- ✓ API key authentication
- ✓ IAM least privilege
- ✓ No public access

**Exit Codes:**
- `0` - All security checks passed
- `1` - Security issues found

**Estimated Time:** 30 seconds

**See Also:** `docs/SECURITY.md`, `docs/IAM_PERMISSIONS.md`

---

### 6. deploy_dashboard.sh - Dashboard Deployment (Amplify)

Builds and prepares the React dashboard for deployment to AWS Amplify.

**Usage:**
```bash
./scripts/deploy_dashboard.sh
```

**What it does:**
1. Checks prerequisites (Node.js, npm, AWS CLI, jq)
2. Retrieves Terraform outputs (API URL, API Key, Amplify App ID)
3. Installs dashboard dependencies
4. Configures environment variables for production
5. Builds the React application
6. Creates deployment package (dashboard-build.zip)
7. Uploads build artifacts to S3
8. Provides deployment options and instructions

**Deployment Options:**
- **Option 1:** Manual upload via Amplify Console
- **Option 2:** S3 + CloudFront hosting (see deploy_dashboard_s3.sh)
- **Option 3:** Connect to Git repository for auto-deployment

**Prerequisites:**
- Node.js >= 18
- npm
- AWS CLI configured
- jq (JSON processor)
- Terraform infrastructure deployed

**Estimated Time:** 2-3 minutes

---

### 7. deploy_dashboard_s3.sh - Dashboard S3 Deployment (Simple)

Deploys the React dashboard directly to S3 for static website hosting (simpler alternative to Amplify).

**Usage:**
```bash
./scripts/deploy_dashboard_s3.sh
```

**What it does:**
1. Checks prerequisites
2. Retrieves Terraform outputs
3. Installs dashboard dependencies
4. Builds the React application
5. Creates/configures S3 bucket for static website hosting
6. Sets bucket policy for public read access
7. Uploads build files to S3 with appropriate cache headers
8. Provides website URL

**Features:**
- Simpler than Amplify (no additional AWS service)
- Very low cost (~$0.50/month)
- HTTP endpoint (HTTPS requires CloudFront)
- Automatic cache control headers
- Public read access for static files

**Prerequisites:**
- Node.js >= 18
- npm
- AWS CLI configured
- Terraform infrastructure deployed

**Cost:** ~$0.50/month (S3 storage + requests)

**Estimated Time:** 2-3 minutes

---

## Typical Workflow

### Initial Deployment
```bash
# 1. Deploy infrastructure
./scripts/setup.sh

# 2. Download IoT certificates from AWS Console
# Save to: simulator/certs/

# 3. Run simulator
cd simulator
python simulator.py

# 4. Deploy dashboard (choose one option)
# Option A: Simple S3 deployment (recommended for prototype)
./scripts/deploy_dashboard_s3.sh

# Option B: Amplify deployment (for production-like setup)
./scripts/deploy_dashboard.sh
```

### Cost Monitoring
```bash
# Check costs weekly
./scripts/check_costs.sh
```

### Security Verification
```bash
# Verify security configuration after deployment
./scripts/verify_security.sh
```

### Complete Teardown
```bash
# When done testing
./scripts/teardown.sh

# Verify cleanup
./scripts/verify_cleanup.sh
```

---

## Script Outputs

### setup.sh Output File
Creates `.deployment_outputs` with:
```bash
API_URL=https://xxxxx.execute-api.us-east-1.amazonaws.com/demo
API_KEY=xxxxxxxxxxxxxxxxxxxxx
IOT_ENDPOINT=xxxxx-ats.iot.us-east-1.amazonaws.com
IOT_THING_NAME=kia-paintshop-simulator
REGION=us-east-1
DEPLOYED_AT=2026-02-19T12:00:00Z
```

### check_costs.sh Output
- Total cost summary
- Service breakdown table
- Monthly projection
- Budget status with color coding
- Optimization recommendations

### verify_cleanup.sh Output
- Resource-by-resource verification
- List of any remaining resources
- Manual cleanup commands if needed

---

## Environment Variables

Scripts respect these environment variables:

- `AWS_REGION` - AWS region (default: us-east-1)
- `AWS_PROFILE` - AWS CLI profile to use
- Standard AWS credentials environment variables

---

## Troubleshooting

### setup.sh fails with "AWS credentials not configured"
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

### teardown.sh fails to empty S3 bucket
```bash
# Manually empty bucket
aws s3 rm s3://BUCKET_NAME --recursive --force
```

### check_costs.sh shows "No cost data available"
- Cost Explorer data may take 24 hours to appear
- Ensure Cost Explorer is enabled in AWS Console
- Check that you have permissions to access Cost Explorer API

### verify_cleanup.sh finds remaining resources
- Review the listed resources
- Manually delete via AWS Console or CLI
- Some resources may be in different regions
- IoT certificates may need manual deactivation before deletion

---

## Cost Optimization Tips

1. **Run teardown when not testing** - Avoid unnecessary charges
2. **Monitor costs weekly** - Use `check_costs.sh` regularly
3. **Set CloudWatch retention to 7 days** - Reduce log storage costs
4. **Use on-demand billing** - No upfront costs for DynamoDB
5. **Enable S3 lifecycle policies** - Automatic archival to Glacier

---

## Security Notes

- Scripts never commit sensitive data to git
- `.deployment_outputs` is gitignored
- API keys are stored as Terraform sensitive outputs
- IoT certificates should be stored securely
- Always run `verify_cleanup.sh` after teardown to prevent residual charges

---

## Support

For issues or questions:
1. Check `docs/TROUBLESHOOTING.md`
2. Review script output for error messages
3. Verify AWS credentials and permissions
4. Check AWS Console for resource status

---

**Last Updated:** February 19, 2026  
**Version:** 1.0.0
