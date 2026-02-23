# Storage Issue Fix

## Problem
Railway uses ephemeral storage - files saved to disk are lost on container restart. This causes:
- 404 errors when checking paper status
- Frontend spinning forever
- Lost processing results

## Solution Options

### Option 1: Railway Volume (Recommended for MVP)
**Pros:** Simple, no code changes needed
**Cons:** Limited to 1GB free tier, slower than database

**Steps:**
1. Go to Railway dashboard: https://railway.app/project/08a9b702-1f58-4e74-8c63-6bd7da4c6b95
2. Click your service → Volumes tab
3. Add new volume with mount path: `/data`
4. Set environment variable: `DATA_DIR=/data/papers`
5. Redeploy

### Option 2: PostgreSQL Database (Better for Production)
**Pros:** Reliable, scalable, better for production
**Cons:** Requires code changes

**Implementation:**
1. Add PostgreSQL to Railway project
2. Install `psycopg2` or `sqlalchemy`
3. Replace file storage with database tables:
   - `papers` table: paper_id, status, data, created_at, updated_at
   - Store JSON data in JSONB column
4. Update `storage.py` to use database instead of files

### Option 3: Redis (Fast but requires paid plan)
**Pros:** Very fast, good for temporary data
**Cons:** Costs money, data expires

## Immediate Fix

Since Railway CLI has issues, you need to manually add the volume:

1. **Add Volume via Dashboard:**
   - Mount path: `/data`
   - This persists across restarts

2. **Update Environment Variable:**
   ```bash
   DATA_DIR=/data/papers
   ```

3. **Redeploy:**
   ```bash
   railway up
   ```

## Testing After Fix

1. Upload a PDF
2. Check logs: `railway logs --tail 100`
3. Verify file persists: `railway run ls -la /data/papers/`
4. Restart service and verify files still exist

## Long-term Recommendation

For production, migrate to PostgreSQL:
- More reliable than file storage
- Better for concurrent access
- Easier to backup
- Can query/filter papers
- No storage limits

Would you like me to implement the PostgreSQL solution?
