---
inclusion: always
---

# Product Overview

KIA Paint Shop IoT Prototype - A serverless AWS solution for digitalizing and monitoring 100 variables from KIA's paint shop manufacturing process.

## Purpose

Demonstrate the viability of paint shop digitalization using AWS IoT services while maintaining strict cost controls (<$50/month). This is a prototype, not a production system.

## Key Constraints

- Budget: <$50 USD/month (actual: ~$1.50/month)
- Variables: Maximum 100 simultaneous variables
- Frequency: 30-second intervals (not extreme real-time)
- Retention: 30 days in DynamoDB, 90 days in S3
- Users: <10 concurrent dashboard users
- Infrastructure: Must be fully ephemeral (create/destroy on demand)

## Variable Categories

- Pre-Treatment (PT): 48 variables
- E-Coat (ED): 18 variables  
- Production Control: 34 variables
- Total: ~100 variables for prototype

## Architecture Pattern

Event-driven serverless architecture:
```
Simulator → IoT Core → Lambda (Ingest) → DynamoDB
                     ↓
                EventBridge → Lambda (Process) → Alarms
                     ↓
                Lambda (Statistics) → Aggregations
                     ↓
                API Gateway → React Dashboard
```

## Success Criteria

- Demonstrate AWS IoT capabilities
- Prove cost-effectiveness
- Show scalability potential
- Enable complete teardown without residual charges
