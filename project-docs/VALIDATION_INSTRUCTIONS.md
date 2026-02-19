# How to Run the Complete Validation Guide

**Task 20: Final System Validation**

You've chosen to run the complete validation guide before final acceptance. This is the recommended approach for thorough system verification.

---

## Quick Start

### Prerequisites Check

Before starting, verify you have:

```bash
# Check AWS CLI
aws --version
# Expected: aws-cli/2.x.x or higher

# Check Terraform
terraform --version
# Expected: Terraform v1.5.0 or higher

# Check Python
python3 --version
# Expected: Python 3.11 or higher

# Check Node.js
node --version
npm --version
# Expected: Node v18+ and npm v9+

# Verify AWS credentials
aws sts get-caller-identity
# Should return your AWS account details
```

---

## Validation Approach

### Option 1: Full Validation (Recommended - 3-4 hours)

Follow **FINAL_VALIDATION_GUIDE.md** step-by-step through all 11 phases:

```bash
# Open the guide
cat FINAL_VALIDATION_GUIDE.md

# Or view in your editor
code FINAL_VALIDATION_GUIDE.md
```

**Phases:**
1. Infrastructure Deployment (30-45 min)
2. Simulator Setup (15-20 min)
3. Backend Pipeline Verification (10-15 min)
4. API Testing (15-20 min)
5. Dashboard Testing (20-30 min)
6. Cost Verification (10 min)
7. End-to-End Integration (15 min)
8. Performance Testing (10 min)
9. Security Verification (10 min)
10. Teardown and Cleanup (15-20 min)
11. Requirements Validation Checklist

### Option 2: Quick Validation (30-45 minutes)

For a faster validation focusing on core functionality:

```bash
# 1. Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply -auto-approve

# 2. Get outputs
export API_URL=$(terraform output -raw api_url)
export API_KEY=$(terraform output -raw api_key)
export IOT_ENDPOINT=$(terraform output -raw iot_endpoint)

# 3. Configure simulator
cd ../simulator
# Update config.yaml with $IOT_ENDPOINT
# Download certificates from AWS IoT Console

# 4. Run simulator (2 minutes)
python simulator.py --config config.yaml
# Press Ctrl+C after 2 minutes

# 5. Test API
curl -X GET "$API_URL/variables" -H "x-api-key: $API_KEY" | jq

# 6. Start dashboard
cd ../dashboard
echo "REACT_APP_API_URL=$API_URL" > .env
echo "REACT_APP_API_KEY=$API_KEY" >> .env
npm install
npm start
# Opens browser at http://localhost:3000

# 7. Verify in browser
# - Check variables list loads
# - Select a variable and view chart
# - Check alarms panel

# 8. Teardown
cd ../terraform
terraform destroy -auto-approve

# 9. Verify cleanup
cd ..
bash scripts/verify_cleanup.sh
```

---

## Validation Checklist

As you go through the validation, check off each item:

### Infrastructure
- [ ] Terraform apply succeeds without errors
- [ ] All 50+ resources created
- [ ] Outputs available (API URL, API key, IoT endpoint)
- [ ] DynamoDB tables exist (4 tables)
- [ ] Lambda functions deployed (8 functions)
- [ ] API Gateway configured
- [ ] IoT Thing and certificates created

### Simulator
- [ ] Certificates downloaded and configured
- [ ] Simulator connects to IoT Core
- [ ] Messages published successfully
- [ ] No connection errors in logs

### Backend Pipeline
- [ ] Data appears in DynamoDB sensor-data table
- [ ] Lambda ingest logs show successful processing
- [ ] Lambda process generates alarms (if thresholds exceeded)
- [ ] Lambda statistics runs every 5 minutes
- [ ] Statistics appear in DynamoDB statistics table

### API
- [ ] GET /variables returns 97 variables
- [ ] GET /variables/{id}/data returns historical data
- [ ] GET /alarms returns alarms
- [ ] POST /alarms/{id}/acknowledge updates alarm status
- [ ] GET /statistics/{variable_id} returns statistics
- [ ] API authentication works (401 without API key)

### Dashboard
- [ ] Dashboard loads without errors
- [ ] Variable list displays 97 variables
- [ ] Variables organized by area (Pre-Treatment, E-Coat, Production Control)
- [ ] Selecting variable shows chart
- [ ] Chart displays last 60 minutes of data
- [ ] Alarm panel shows active alarms
- [ ] Acknowledge button works
- [ ] Statistics card shows aggregated data
- [ ] Auto-refresh works (every 30 seconds)
- [ ] Connection status indicator works

### Cost
- [ ] Projected monthly cost < $50
- [ ] Cost breakdown shows $1-5/month
- [ ] CloudWatch alarms configured
- [ ] Usage within free tier limits

### Security
- [ ] API requires authentication
- [ ] IoT requires X.509 certificates
- [ ] S3 bucket blocks public access
- [ ] DynamoDB encryption enabled
- [ ] IAM roles follow least privilege

### Teardown
- [ ] Terraform destroy succeeds
- [ ] All resources removed
- [ ] No orphaned resources (verified by script)
- [ ] No residual costs

---

## Troubleshooting During Validation

If you encounter issues, refer to the **Troubleshooting Guide** section in FINAL_VALIDATION_GUIDE.md.

Common issues and quick fixes:

### Simulator won't connect
```bash
# Check IoT endpoint
echo $IOT_ENDPOINT

# Verify certificates exist
ls -la simulator/certs/

# Check IoT policy in AWS console
# Ensure it allows publish to kia/paintshop/*
```

### No data in DynamoDB
```bash
# Check Lambda logs
aws logs tail /aws/lambda/kia-paintshop-ingest-demo --follow

# Verify IoT Rule is enabled
aws iot get-topic-rule --rule-name kia_paintshop_ingest_rule
```

### Dashboard shows no data
```bash
# Check .env file
cat dashboard/.env

# Test API directly
curl -X GET "$API_URL/variables" -H "x-api-key: $API_KEY"

# Check browser console for errors
# Open DevTools → Console
```

---

## After Validation

Once you complete the validation:

1. **Document any issues** you encountered
2. **Note which components worked well**
3. **Identify any concerns or questions**
4. **Decide if the system meets your requirements**

Then, I can help you with:
- Fixing any issues found
- Deploying dashboard to production (Task 14)
- Adding optional enhancements (Tasks 14-19)
- Preparing for demonstration to stakeholders

---

## Getting Help

If you need assistance during validation:

1. **Check the troubleshooting section** in FINAL_VALIDATION_GUIDE.md
2. **Review CloudWatch logs** for error details
3. **Run verification scripts** in the scripts/ directory
4. **Ask me specific questions** about any component

---

## Validation Timeline

**Estimated Time:**
- Full validation: 3-4 hours
- Quick validation: 30-45 minutes

**Recommendation:** Set aside a dedicated time block to avoid interruptions.

---

**Ready to start?** Open FINAL_VALIDATION_GUIDE.md and begin with Phase 1: Infrastructure Deployment.

Good luck with the validation! 🚀
