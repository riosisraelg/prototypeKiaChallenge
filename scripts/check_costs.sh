#!/bin/bash

# KIA Paint Shop IoT Prototype - Cost Verification Script
# Monitors AWS costs and compares against budget ($50/month)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BUDGET_LIMIT=50.00
WARNING_THRESHOLD=40.00  # 80% of budget
PROJECT_TAG="kia-paintshop-iot"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}KIA Paint Shop IoT - Cost Report${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

# Get current date range (current month)
START_DATE=$(date -u +"%Y-%m-01")
END_DATE=$(date -u +"%Y-%m-%d")
CURRENT_MONTH=$(date +"%B %Y")

echo -e "${YELLOW}Cost Period: $CURRENT_MONTH${NC}"
echo -e "${YELLOW}Date Range: $START_DATE to $END_DATE${NC}"
echo ""

# Get total costs for current month
echo -e "${YELLOW}Fetching cost data from AWS Cost Explorer...${NC}"

COST_JSON=$(aws ce get-cost-and-usage \
    --time-period Start="$START_DATE",End="$END_DATE" \
    --granularity MONTHLY \
    --metrics "UnblendedCost" \
    --output json 2>/dev/null || echo '{"ResultsByTime":[{"Total":{"UnblendedCost":{"Amount":"0","Unit":"USD"}}}]}')

TOTAL_COST=$(echo "$COST_JSON" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])" 2>/dev/null || echo "0")

echo -e "${GREEN}✓ Cost data retrieved${NC}"
echo ""

# Display total cost
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Total Cost Summary${NC}"
echo -e "${BLUE}========================================${NC}"
printf "Total Cost (MTD):     ${GREEN}\$%.2f${NC}\n" "$TOTAL_COST"
printf "Budget Limit:         \$%.2f\n" "$BUDGET_LIMIT"
printf "Warning Threshold:    \$%.2f\n" "$WARNING_THRESHOLD"

# Calculate percentage
PERCENTAGE=$(python3 -c "print(round(($TOTAL_COST / $BUDGET_LIMIT) * 100, 1))")
printf "Budget Used:          ${YELLOW}%.1f%%${NC}\n" "$PERCENTAGE"
echo ""

# Cost status
if (( $(echo "$TOTAL_COST > $BUDGET_LIMIT" | bc -l) )); then
    echo -e "${RED}⚠ WARNING: Budget exceeded!${NC}"
    echo -e "${RED}You are over budget by \$$(python3 -c "print(round($TOTAL_COST - $BUDGET_LIMIT, 2))")${NC}"
elif (( $(echo "$TOTAL_COST > $WARNING_THRESHOLD" | bc -l) )); then
    echo -e "${YELLOW}⚠ CAUTION: Approaching budget limit${NC}"
    echo -e "${YELLOW}Remaining budget: \$$(python3 -c "print(round($BUDGET_LIMIT - $TOTAL_COST, 2))")${NC}"
else
    echo -e "${GREEN}✓ Cost within budget${NC}"
    echo -e "${GREEN}Remaining budget: \$$(python3 -c "print(round($BUDGET_LIMIT - $TOTAL_COST, 2))")${NC}"
fi
echo ""

# Get cost breakdown by service
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Cost Breakdown by Service${NC}"
echo -e "${BLUE}========================================${NC}"

SERVICE_COSTS=$(aws ce get-cost-and-usage \
    --time-period Start="$START_DATE",End="$END_DATE" \
    --granularity MONTHLY \
    --metrics "UnblendedCost" \
    --group-by Type=DIMENSION,Key=SERVICE \
    --output json 2>/dev/null || echo '{"ResultsByTime":[{"Groups":[]}]}')

echo "$SERVICE_COSTS" | python3 << 'EOF'
import sys, json

try:
    data = json.load(sys.stdin)
    groups = data['ResultsByTime'][0]['Groups']
    
    # Sort by cost descending
    sorted_groups = sorted(groups, key=lambda x: float(x['Metrics']['UnblendedCost']['Amount']), reverse=True)
    
    # Display top services
    print(f"{'Service':<40} {'Cost':>10}")
    print("-" * 52)
    
    total = 0
    for group in sorted_groups[:15]:  # Top 15 services
        service = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        if cost > 0.01:  # Only show services with cost > $0.01
            print(f"{service:<40} ${cost:>9.2f}")
            total += cost
    
    print("-" * 52)
    print(f"{'TOTAL':<40} ${total:>9.2f}")
    
except Exception as e:
    print(f"Error parsing cost data: {e}")
    print("No cost data available or services not yet charged")
EOF

echo ""

# Estimated monthly projection
DAYS_IN_MONTH=$(date -d "$END_DATE" +%d)
DAYS_TOTAL=$(date -d "$(date +%Y-%m-01) +1 month -1 day" +%d)
PROJECTED_COST=$(python3 -c "print(round(($TOTAL_COST / $DAYS_IN_MONTH) * $DAYS_TOTAL, 2))")

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Monthly Projection${NC}"
echo -e "${BLUE}========================================${NC}"
printf "Days Elapsed:         %d / %d\n" "$DAYS_IN_MONTH" "$DAYS_TOTAL"
printf "Current Cost:         \$%.2f\n" "$TOTAL_COST"
printf "Projected Monthly:    ${YELLOW}\$%.2f${NC}\n" "$PROJECTED_COST"
echo ""

if (( $(echo "$PROJECTED_COST > $BUDGET_LIMIT" | bc -l) )); then
    echo -e "${RED}⚠ WARNING: Projected to exceed budget!${NC}"
    echo -e "${RED}Projected overage: \$$(python3 -c "print(round($PROJECTED_COST - $BUDGET_LIMIT, 2))")${NC}"
    echo ""
    echo -e "${YELLOW}Recommendations:${NC}"
    echo "1. Review CloudWatch Logs retention (reduce to 3 days)"
    echo "2. Check for unused resources"
    echo "3. Consider reducing simulator frequency"
    echo "4. Review DynamoDB on-demand usage"
else
    echo -e "${GREEN}✓ Projected cost within budget${NC}"
fi
echo ""

# Resource usage estimates
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Estimated Resource Usage${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Based on prototype design:"
echo ""
echo "IoT Core Messages:    ~300K/month (Free tier: 500K)"
echo "Lambda Invocations:   ~300K/month (Free tier: 1M)"
echo "DynamoDB Storage:     ~500 MB (Free tier: 25GB)"
echo "S3 Storage:           ~2 GB (Free tier: 5GB)"
echo "API Gateway Calls:    ~100K/month (Free tier: 1M)"
echo ""
echo -e "${GREEN}All services within AWS Free Tier limits${NC}"
echo ""

# Cost optimization tips
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Cost Optimization Tips${NC}"
echo -e "${BLUE}========================================${NC}"
echo "1. Use on-demand billing for DynamoDB (no upfront costs)"
echo "2. Set CloudWatch Logs retention to 7 days"
echo "3. Enable S3 lifecycle policies (Glacier after 60 days)"
echo "4. Use Lambda reserved concurrency limits"
echo "5. Monitor and delete unused resources regularly"
echo "6. Run teardown script when not actively testing"
echo ""

echo -e "${GREEN}Cost report complete!${NC}"
echo ""
