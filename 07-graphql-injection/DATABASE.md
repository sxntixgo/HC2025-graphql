# Database Configuration

## Read-Only Database Protection

This challenge uses a **read-only SQLite database** to prevent players from accidentally or intentionally dropping tables, deleting data, or modifying database contents. The SQL injection vulnerability is preserved for learning purposes, but destructive operations are blocked.

## How It Works

### 1. Database Initialization

The database is created during Docker image build:

```bash
node init-db.js
```

This script:
- Creates `/app/data/challenge.db`
- Sets up tables (users, documents)
- Seeds initial data including the FLAG
- Sets file permissions to read-only (444)

### 2. Read-Only Mode

The application opens the database with `sqlite3.OPEN_READONLY` flag:

```javascript
const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY);
```

This prevents:
- `DROP TABLE` statements
- `DELETE FROM` operations
- `UPDATE` statements
- `INSERT` operations
- `ALTER TABLE` commands

### 3. File System Protection

The database file has OS-level read-only permissions:
- Database file: `444` (r--r--r--)
- Data directory: `555` (r-xr-xr-x)

## Local Development

### Initialize Database Locally

```bash
cd 07-graphql-injection
FLAG="your_flag_here" node init-db.js
```

### Re-initialize with New Flag

```bash
# Remove old database
rm -rf data/

# Create new database with updated flag
FLAG="new_flag_value" node init-db.js
```

## Docker Build

### Development Build

```bash
docker-compose -f docker-compose-dev.yml build
```

The FLAG from `.env` file is embedded during build.

### Production Build

```bash
docker-compose build --build-arg FLAG="production_flag_value"
```

## Security Benefits

1. **Prevents Destructive Operations**: Players cannot break the challenge for others
2. **Maintains Vulnerability**: SQL injection still works for data exfiltration
3. **Auto-Recovery**: Container restart brings back clean database
4. **Multi-Player Safe**: Multiple players can exploit simultaneously

## What Players Can Still Do

✅ Read all data via UNION injection
✅ Bypass authentication/authorization checks
✅ Extract confidential information
✅ Use SQL injection to get the FLAG

❌ Cannot drop tables
❌ Cannot delete data
❌ Cannot modify existing records
❌ Cannot insert new data

## Verification

Check database permissions:
```bash
docker exec -it graphql-injection-app ls -la /app/data/
```

Expected output:
```
dr-xr-xr-x    2 root     root          4096 Oct 12 00:00 .
drwxr-xr-x    1 root     root          4096 Oct 12 00:00 ..
-r--r--r--    1 root     root         16384 Oct 12 00:00 challenge.db
```

Test read-only enforcement:
```bash
docker exec -it graphql-injection-app sqlite3 /app/data/challenge.db "DELETE FROM users;"
```

Expected error:
```
Error: attempt to write a readonly database
```
