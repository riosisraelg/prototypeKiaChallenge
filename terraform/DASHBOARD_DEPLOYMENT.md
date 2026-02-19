# Dashboard Deployment Configuration

## Overview

This document describes the dashboard deployment configuration for the KIA Paint Shop IoT Prototype. The React + TypeScript dashboard can be deployed using two methods:

1. **AWS Amplify** - Production-like setup with automatic builds and HTTPS
2. **S3 Static Hosting** - Simpler, lower-cost option for prototypes

## Terraform Configuration

### Amplify Resources (amplify.tf)

The Terraform configuration creates:

- **AWS Amplify App**: Hosts the React dashboard
- **Amplify Branch**: Main branch for deployment
- **Environment Variables**: Automatically configured with API URL and API Key
- **Build Settings**: Configured for React build process
- **Custom Rules**: SPA routing support (404 → index.html)

### Outputs

The following outputs are available after `terraform apply`:

```bash
amplify_app_id          # Amplify application ID
amplify_app_arn         # Amplify application ARN
amplify_default_domain  # Default Amplify domain
amplify_app_url         # Full URL to dashboard (https://main.{domain})
```

## Deployment Methods

### Method 1: S3 Static Hosting (Recommended for Prototype)

**Advantages:**
- Simplest deployment process
- Lowest cost (~$0.50/month)
- No additional AWS services required
- Fast deployment

**Disadvantages:**
- HTTP only (HTTPS requires CloudFront)
- No automatic builds from Git
- Manual deployment process

**Usage:**
```bash
./scripts/deploy_dashboard_s3.sh
```

**What it does:**
1. Builds the React application
2. Creates S3 bucket: `kia-paintshop-dashboard-{account-id}`
3. Configures bucket for static website hosting
4. Sets public read access policy
5. Uploads build files with cache headers
6. Provides website URL

**Cost:** ~$0.50/month
- S3 storage: ~$0.02/month (100MB)
- S3 requests: ~$0.40/month (100K requests)
- Data transfer: ~$0.08/month (1GB)

**Website URL Format:**
```
http://kia-paintshop-dashboard-{account-id}.s3-website-{region}.amazonaws.com
```

### Method 2: AWS Amplify (Production-like)

**Advantages:**
- HTTPS by default
- Custom domain support
- Git integration for auto-deployment
- Built-in CI/CD
- Preview deployments

**Disadvantages:**
- More complex setup
- Slightly higher cost (still within free tier)
- Requires manual upload or Git connection

**Usage:**
```bash
./scripts/deploy_dashboard.sh
```

**What it does:**
1. Builds the React application
2. Creates deployment package (dashboard-build.zip)
3. Uploads artifacts to S3
4. Provides deployment options:
   - Manual upload via Amplify Console
   - Git repository connection
   - S3 deployment alternative

**Cost:** Free tier eligible
- Amplify hosting: Free for small apps
- Build minutes: 1000 minutes/month free
- Data transfer: 15GB/month free

**Website URL Format:**
```
https://main.{amplify-app-id}.amplifyapp.com
```

## Environment Variables

Both deployment methods automatically configure:

```bash
REACT_APP_API_URL      # API Gateway endpoint
REACT_APP_API_KEY      # API authentication key
GENERATE_SOURCEMAP     # Disabled for security
```

These are retrieved from Terraform outputs and injected during build.

## Build Process

The React build process:

1. **Install Dependencies**: `npm ci`
2. **Configure Environment**: Create `.env.production`
3. **Build Application**: `npm run build`
4. **Optimize Assets**: Minification, tree-shaking, code splitting
5. **Generate Artifacts**: Static files in `build/` directory

**Build Output:**
```
build/
├── index.html           # Entry point (no-cache)
├── static/
│   ├── css/            # Minified CSS (cache: 1 year)
│   ├── js/             # Minified JS bundles (cache: 1 year)
│   └── media/          # Images, fonts (cache: 1 year)
├── manifest.json       # PWA manifest
└── robots.txt          # SEO configuration
```

## Cache Strategy

### S3 Deployment
- **index.html**: `no-cache, no-store, must-revalidate`
- **Static assets**: `public, max-age=31536000` (1 year)

### Amplify Deployment
- Automatic cache headers
- CloudFront CDN integration
- Edge caching for global performance

## Security Considerations

### S3 Deployment
- Public read access required for website hosting
- API key embedded in JavaScript (acceptable for prototype)
- HTTP only (consider CloudFront for HTTPS)
- No authentication on dashboard itself

### Amplify Deployment
- HTTPS by default (TLS 1.2+)
- API key embedded in JavaScript
- CloudFront CDN with AWS Shield Standard
- Optional: Add Cognito authentication

### API Key Security
The API key is embedded in the JavaScript bundle. This is acceptable for a prototype because:
- API has rate limiting (100 req/s)
- Usage plan limits (1000 req/day)
- Read-only operations for most endpoints
- Cost controls prevent abuse

For production, consider:
- Cognito user authentication
- API key rotation
- Request signing
- Backend-for-frontend pattern

## Deployment Workflow

### Initial Deployment

```bash
# 1. Deploy infrastructure (includes Amplify config)
cd terraform
terraform apply

# 2. Deploy dashboard (choose method)
cd ..
./scripts/deploy_dashboard_s3.sh    # Simple S3 hosting
# OR
./scripts/deploy_dashboard.sh       # Amplify hosting

# 3. Access dashboard
# URL provided in script output
```

### Updates

```bash
# Make changes to dashboard code
cd dashboard/src
# ... edit files ...

# Rebuild and redeploy
cd ../..
./scripts/deploy_dashboard_s3.sh    # Rebuilds and uploads
```

### Teardown

```bash
# S3 deployment cleanup
aws s3 rb s3://kia-paintshop-dashboard-{account-id} --force

# Amplify cleanup (handled by Terraform)
cd terraform
terraform destroy
```

## Troubleshooting

### Build Fails

**Error: "npm ci failed"**
```bash
cd dashboard
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Error: "REACT_APP_API_URL not set"**
- Ensure Terraform has been applied
- Check `terraform output api_url`
- Verify `.env.production` file exists

### Deployment Fails

**Error: "Bucket already exists"**
- Bucket names are globally unique
- Script uses account ID to ensure uniqueness
- If error persists, manually delete bucket and retry

**Error: "Access Denied"**
- Check AWS credentials: `aws sts get-caller-identity`
- Verify IAM permissions for S3/Amplify
- Ensure correct AWS region

### Dashboard Not Loading

**Blank page or errors:**
1. Check browser console for errors
2. Verify API URL is correct: `curl $API_URL/variables`
3. Check API key is valid
4. Verify CORS is enabled on API Gateway

**API calls failing:**
1. Check API Gateway endpoint is accessible
2. Verify API key in request headers
3. Check CloudWatch logs for Lambda errors
4. Test API directly with curl

## Cost Optimization

### S3 Hosting
- Enable S3 Intelligent-Tiering for infrequent access
- Set lifecycle policy to delete old versions
- Use CloudFront only if HTTPS required

### Amplify Hosting
- Stay within free tier limits:
  - Build minutes: <1000/month
  - Data transfer: <15GB/month
  - Storage: <5GB
- Disable preview deployments if not needed
- Use manual deployment instead of Git integration

## Monitoring

### S3 Metrics
```bash
# Check bucket size
aws s3 ls s3://kia-paintshop-dashboard-{account-id} --recursive --summarize

# Check request metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name NumberOfObjects \
  --dimensions Name=BucketName,Value=kia-paintshop-dashboard-{account-id}
```

### Amplify Metrics
- View in Amplify Console
- Build history and logs
- Traffic and bandwidth usage
- Error rates

## Next Steps

After deployment:

1. **Test Dashboard**: Open URL and verify all features work
2. **Monitor Costs**: Run `./scripts/check_costs.sh`
3. **Document URL**: Save dashboard URL for team access
4. **Set Up Monitoring**: Configure CloudWatch alarms if needed
5. **Plan Updates**: Establish update/deployment schedule

## References

- [AWS Amplify Documentation](https://docs.aws.amazon.com/amplify/)
- [S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

---

**Last Updated:** February 19, 2026  
**Version:** 1.0.0  
**Task:** 14 - Dashboard Deployment Configuration
