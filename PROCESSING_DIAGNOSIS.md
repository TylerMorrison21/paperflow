# Processing Issue Diagnosis

## Issue
Frontend shows continuous spinning during PDF conversion - nothing happens.

## What We've Done

### 1. Added Detailed Logging ✅
- Marker API upload/polling logs
- Processing pipeline stage tracking
- Error logging with full stack traces
- Timestamps for each stage

### 2. Improved Error Handling ✅
- Better validation for empty/None markdown
- Clear error messages for invalid PDFs
- Error codes propagated to frontend

### 3. Deployment ✅
- Logging improvements deployed to Railway
- Health check passing
- Ready to diagnose

## How to Diagnose

### Step 1: Upload a PDF
1. Go to https://frontend-one-alpha-89.vercel.app
2. Upload a real academic PDF (not a test file)
3. Note the paper_id from the URL (e.g., /read/abc-123-def)

### Step 2: Check Logs
```bash
railway logs --tail 100
```

Look for:
- `New upload: paper_id=...` - Upload received
- `Starting PDF parse, size: X bytes` - Marker API starting
- `Uploading PDF to Marker API...` - Upload to Marker
- `Upload response: {...}` - Marker accepted
- `Polling status at: ...` - Polling started
- `Poll #1: status=processing` - Marker processing
- `Poll #N: status=complete` - Marker done
- `Marker API processing complete` - Success
- `Postprocessing complete` - Done

### Step 3: Check Status Manually
```bash
curl https://pdfreflow-production.up.railway.app/api/parse/{paper_id}
```

## Common Issues

### Issue 1: Marker API Timeout (600s)
**Symptom:** Logs show many polls but never complete
**Cause:** PDF too complex, Marker API overloaded
**Solution:** Increase POLL_TIMEOUT or retry

### Issue 2: Invalid PDF
**Symptom:** Error "Marker API returned empty or None markdown"
**Cause:** PDF is corrupted, scanned image, or unsupported format
**Solution:** Try different PDF

### Issue 3: Railway Storage Issue
**Symptom:** 404 errors when checking status
**Cause:** Task file not persisting (Railway ephemeral storage)
**Solution:** Use Railway volume or database

### Issue 4: DATALAB_API_KEY Issue
**Symptom:** "DATALAB_API_KEY is not set" error
**Cause:** Environment variable missing
**Solution:** Check Railway environment variables

### Issue 5: Frontend Polling Issue
**Symptom:** Backend completes but frontend keeps spinning
**Cause:** Frontend not detecting completion
**Solution:** Check browser console for errors

## Next Steps

1. **Upload a PDF** through the frontend
2. **Share the paper_id** so I can check logs
3. **Check browser console** for any JavaScript errors
4. **Wait 2-3 minutes** (normal processing time)

## Expected Timeline

- Upload: < 1 second
- Marker API upload: 2-5 seconds
- Marker API processing: 30-120 seconds (depends on PDF)
- Postprocessing: 1-2 seconds
- Total: 30-130 seconds for typical academic paper

## Monitoring Commands

```bash
# Watch logs live
railway logs --follow

# Check specific paper
curl https://pdfreflow-production.up.railway.app/api/parse/{paper_id}

# Check recent papers
ls -lht data/papers/*.json | head -5
```
