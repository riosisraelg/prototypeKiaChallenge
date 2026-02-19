# Dashboard Verification Guide - Task 15

This guide will walk you through verifying the KIA Paint Shop IoT Dashboard is working correctly.

## Prerequisites

Before starting, ensure you have:
- ✅ Infrastructure deployed (Tasks 1-3)
- ✅ Simulator running and sending data (Tasks 4-5)
- ✅ Lambda functions deployed (Tasks 6-8)
- ✅ API Gateway deployed (Tasks 10-12)
- ✅ Dashboard implemented (Task 13)

## Step 1: Deploy Infrastructure (if not already done)

```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Deploy infrastructure
terraform apply -auto-approve

# Save outputs to file
terraform output -json > outputs.json
```

**Expected Result:** All AWS resources created successfully (IoT Core, DynamoDB, Lambda, API Gateway, etc.)

## Step 2: Get API Configuration

```bash
# From terraform directory, extract API URL and API Key
terraform output api_gateway_url
terraform output api_key

# Or view all outputs
cat outputs.json
```

**Note these values - you'll need them for the dashboard configuration.**

## Step 3: Configure Dashboard Environment

```bash
# Navigate to dashboard directory
cd ../dashboard

# Copy environment template
cp .env.example .env.local

# Edit .env.local with your values
# Replace with actual values from Step 2
```

Edit `.env.local`:
```env
REACT_APP_API_URL=https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/demo
REACT_APP_API_KEY=YOUR_API_KEY_HERE
```

## Step 4: Install Dashboard Dependencies

```bash
# Still in dashboard directory
npm install
```

**Expected Result:** All dependencies installed without errors (~2-3 minutes)

## Step 5: Start the Simulator (if not running)

Open a new terminal:

```bash
# Navigate to simulator directory
cd simulator

# Install Python dependencies (if not done)
pip install -r requirements.txt

# Configure simulator with IoT endpoint
# Edit config.yaml with your IoT endpoint from terraform outputs

# Run simulator
python simulator.py --config config.yaml
```

**Expected Result:** Simulator starts and publishes data every 30 seconds

## Step 6: Start the Dashboard

In the dashboard terminal:

```bash
# Start development server
npm start
```

**Expected Result:** 
- Dashboard compiles successfully
- Browser opens automatically to http://localhost:3000
- No compilation errors in terminal

## Step 7: Verify Variable List

**In the browser:**

1. Dashboard loads without errors
2. Check the left panel shows three sections:
   - **Pre-Treatment** (48 variables)
   - **E-Coat** (18 variables)
   - **Production Control** (34 variables)
3. Each variable shows:
   - Variable ID (e.g., PT-TEMP-001)
   - Name/description
   - Current value with unit
   - Status indicator (active/alarm)

**✅ PASS:** All 100 variables are visible and organized by area
**❌ FAIL:** Variables not loading → Check API connection and API key

## Step 8: Verify Variable Chart

1. Click on any variable in the list (e.g., PT-TEMP-001)
2. Chart appears in the main panel
3. Verify chart shows:
   - Line graph with data points
   - X-axis: Time (last 60 minutes)
   - Y-axis: Value with unit
   - Two horizontal lines (alarm_low and alarm_high thresholds)
   - Legend showing threshold values

4. Wait 30 seconds and verify:
   - Chart auto-refreshes with new data
   - New data points appear on the right
   - Old data points scroll off the left

**✅ PASS:** Chart displays correctly and auto-refreshes
**❌ FAIL:** No data showing → Check if simulator is running and sending data

## Step 9: Verify Statistics Card

Below the chart, verify the statistics card shows:
- **Average:** Calculated average value
- **Min:** Minimum value in time window
- **Max:** Maximum value in time window
- **Std Dev:** Standard deviation

**✅ PASS:** Statistics display with correct units
**❌ FAIL:** Statistics not showing → Check Lambda statistics function

## Step 10: Verify Alarm Panel

In the right panel:

1. Check if any alarms are displayed
2. If no alarms, generate one:
   - Wait for simulator to generate an anomaly (5% probability)
   - OR modify simulator to force an alarm
   - OR manually insert alarm in DynamoDB

3. When alarm appears, verify:
   - Alarm shows variable ID
   - Severity indicator (⚠️ Warning or 🔴 Critical)
   - Timestamp
   - Value that triggered alarm
   - "Acknowledge" button

**✅ PASS:** Alarms display correctly
**❌ FAIL:** Alarms not showing → Check Lambda process function

## Step 11: Verify Alarm Acknowledgment

1. Click "Acknowledge" button on an active alarm
2. Verify:
   - Button shows loading state
   - Alarm status changes to "Acknowledged"
   - Acknowledged timestamp appears
   - Button becomes disabled or changes to "Acknowledged"

3. Filter alarms by status:
   - Click "Active" filter → Shows only active alarms
   - Click "Acknowledged" filter → Shows acknowledged alarms
   - Click "All" → Shows all alarms

**✅ PASS:** Alarm acknowledgment works correctly
**❌ FAIL:** Acknowledgment fails → Check API endpoint and permissions

## Step 12: Verify Connection Status

In the top-right corner:

1. Verify connection indicator shows:
   - 🟢 "Connected" when API is reachable
   - Green dot or checkmark

2. Test error state (optional):
   - Stop API Gateway or change API key to invalid value
   - Verify indicator shows:
     - 🔴 "Disconnected" or "Error"
     - Red dot or error icon

**✅ PASS:** Connection status reflects actual API state
**❌ FAIL:** Status not updating → Check ConnectionStatus component

## Step 13: Verify Auto-Refresh

1. Open browser DevTools (F12)
2. Go to Network tab
3. Watch for API requests every 30 seconds:
   - GET /variables
   - GET /variables/{id}/data
   - GET /alarms
   - GET /statistics/{id}

**✅ PASS:** Requests fire automatically every 30 seconds
**❌ FAIL:** No auto-refresh → Check TanStack Query configuration

## Step 14: Verify Responsive Design (Optional)

1. Resize browser window to mobile size (< 768px)
2. Verify:
   - Layout adapts to smaller screen
   - All components remain usable
   - No horizontal scrolling

**✅ PASS:** Dashboard is responsive
**❌ FAIL:** Layout breaks → Check Tailwind CSS classes

## Troubleshooting Common Issues

### Issue: "Network Error" or "Failed to fetch"

**Cause:** API Gateway not reachable or CORS issue

**Solution:**
1. Verify API URL in `.env.local` is correct
2. Check API Gateway is deployed: `terraform output api_gateway_url`
3. Verify CORS is enabled in API Gateway
4. Check browser console for specific error

### Issue: "401 Unauthorized"

**Cause:** Invalid or missing API key

**Solution:**
1. Verify API key in `.env.local` matches terraform output
2. Check API key is being sent in request headers (DevTools → Network → Headers)
3. Verify API Gateway API key configuration

### Issue: No data in charts

**Cause:** Simulator not running or data not reaching DynamoDB

**Solution:**
1. Check simulator is running: `ps aux | grep simulator`
2. Check simulator logs for errors
3. Verify IoT Core is receiving messages (CloudWatch Logs)
4. Check DynamoDB table has data: `aws dynamodb scan --table-name kia-paintshop-sensor-data --limit 5`

### Issue: Alarms not appearing

**Cause:** Lambda process function not running or no anomalies detected

**Solution:**
1. Check Lambda process function logs (CloudWatch)
2. Verify EventBridge rule is triggering Lambda
3. Manually create test alarm in DynamoDB
4. Increase anomaly probability in simulator config

### Issue: Dashboard won't start (npm start fails)

**Cause:** Missing dependencies or port conflict

**Solution:**
1. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
2. Check port 3000 is not in use: `lsof -i :3000`
3. Try different port: `PORT=3001 npm start`

## Verification Checklist Summary

Mark each item as you verify:

- [ ] Infrastructure deployed successfully
- [ ] Simulator running and sending data
- [ ] Dashboard starts without errors
- [ ] 100 variables display in organized list
- [ ] Variable chart shows data and auto-refreshes
- [ ] Statistics card displays correct values
- [ ] Alarms appear in alarm panel
- [ ] Alarm acknowledgment works
- [ ] Connection status indicator works
- [ ] Auto-refresh happens every 30 seconds

## Success Criteria

**Dashboard verification is COMPLETE when:**
- ✅ All 100 variables are visible and selectable
- ✅ Charts display real-time data with auto-refresh
- ✅ Alarms can be generated and acknowledged
- ✅ Connection status reflects API state
- ✅ No console errors in browser DevTools

## Next Steps

After successful verification:
1. Mark Task 15 as complete
2. Optionally proceed to Task 16 (Management Scripts)
3. Or continue to Task 17 (Monitoring and Alarms)

## Need Help?

If you encounter issues not covered in this guide:
1. Check browser console for errors (F12 → Console)
2. Check API Gateway logs in CloudWatch
3. Check Lambda function logs in CloudWatch
4. Review `dashboard/README.md` for additional details
5. Ask for help with specific error messages
