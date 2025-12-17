# CloudFront Functions for LEH

This directory contains CloudFront Functions for handling dynamic routing in the LEH frontend.

## Dynamic Route Handler

**File:** `dynamic-route-handler.js`

### Purpose

Next.js static export (`output: 'export'`) only generates HTML files for IDs specified in `generateStaticParams`. When users access dynamic case IDs (like `case_e5db1573bb04`) that weren't pre-rendered, S3 returns a 404.

This CloudFront Function solves this by:
1. Detecting requests for case detail paths
2. Rewriting the origin path to serve a pre-rendered fallback page
3. Preserving the original URL in the browser

The client-side JavaScript (`useCaseIdFromUrl` hook) reads the actual URL to get the correct case ID and fetches the appropriate data.

### How It Works

```
User Request: /lawyer/cases/case_abc123/
     ↓
CloudFront Function detects dynamic ID
     ↓
Rewrites origin path to: /lawyer/cases/1/index.html
     ↓
S3 serves the pre-rendered page
     ↓
Browser URL remains: /lawyer/cases/case_abc123/
     ↓
Client-side JS reads URL, extracts "case_abc123"
     ↓
API call fetches correct case data
```

### Deployment Steps

1. **Go to CloudFront Console**
   - Open AWS Console → CloudFront → Functions

2. **Create New Function**
   - Click "Create function"
   - Name: `leh-dynamic-route-handler`
   - Runtime: `cloudfront-js-1.0`

3. **Add Code**
   - Copy the contents of `dynamic-route-handler.js`
   - Paste into the function editor

4. **Publish**
   - Click "Publish"

5. **Associate with Distribution**
   - Go to your CloudFront distribution
   - Click "Behaviors" tab
   - Edit the default behavior (or create a new one for `*/cases/*`)
   - Under "Function associations":
     - Viewer request: Select `leh-dynamic-route-handler`
   - Save changes

### Pre-rendered IDs

The function has a hardcoded list of pre-rendered IDs from `generateStaticParams`:
- `1`, `2`, `3` (development placeholders)
- `test-case-001`, `test-case-empty` (E2E test IDs)

If you add more pre-rendered IDs, update both:
1. `generateStaticParams` in page.tsx files
2. `PRERENDERED_IDS` array in this function

### Testing

After deployment, test these scenarios:

1. **Pre-rendered ID** (should work directly):
   ```
   https://your-domain/lawyer/cases/1/
   ```

2. **Dynamic ID** (should be rewritten but still work):
   ```
   https://your-domain/lawyer/cases/case_e5db1573bb04/
   ```

3. **Sub-routes** (procedure, assets, etc.):
   ```
   https://your-domain/lawyer/cases/case_abc/procedure/
   https://your-domain/lawyer/cases/case_abc/assets/
   ```

### Alternative: S3 Error Document

If you can't use CloudFront Functions (e.g., using S3 website hosting directly), you can configure S3 to serve a custom error page:

1. Create a generic SPA fallback page
2. Configure S3 bucket website hosting:
   - Error document: `index.html` (or custom 404 page)
3. This returns the fallback for ALL 404s, not just case routes

The CloudFront Function approach is more targeted and recommended.
