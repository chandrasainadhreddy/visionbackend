# Binocular Vision App - Debugging Guide

## Issues Identified

### 1. **API Routing Problem**
The Android app calls endpoints like:
- `/api/test/start` 
- `/api/test/ran`
- `/api/test/vrg`
- `/api/test/pur`
- `/api/eye-data`

But the PHP files are located at:
- `/api/test/start.php`
- `/api/test/ran.php`
- `/api/test/vrg.php`
- `/api/test/pur.php`
- `/api/eye-data.php`

**Solution**: Created `.htaccess` file to handle URL rewriting.

### 2. **Response Format Mismatch**
The Android app expects `testId` (camelCase) but the PHP was returning `test_id` (snake_case).

**Solution**: Updated `/api/test/start.php` to return `testId` in the response.

### 3. **Data Flow**
The complete flow should be:
1. User starts test → `startTest()` called → `/api/test/start` → Creates test record in DB
2. During test → `addSample()` called → `/api/eye-data` → Saves eye tracking data
3. Test completes → `submitData()` called → `/api/test/{ran|vrg|pur}` → Calls Flask AI server → Saves results
4. Navigate to AI Analysis screen → Shows "Analyzing..."
5. Navigate to Results screen → Shows classification and score

## Files Modified

### 1. `/binocularai/.htaccess` (CREATED)
```apache
RewriteEngine On
RewriteBase /binocularai/

# API routing - remove .php extension
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^api/test/start$ api/test/start.php [L]
RewriteRule ^api/test/ran$ api/test/ran.php [L]
RewriteRule ^api/test/vrg$ api/test/vrg.php [L]
RewriteRule ^api/test/pur$ api/test/pur.php [L]
RewriteRule ^api/eye-data$ api/eye-data.php [L]
```

### 2. `/binocularai/api/test/start.php` (MODIFIED)
Changed line 47 from:
```php
"test_id" => $test_id,
```
to:
```php
"testId" => $test_id,
```

## Testing Steps

### Step 1: Verify Apache mod_rewrite is enabled
1. Open `C:\xampp\apache\conf\httpd.conf`
2. Find the line: `#LoadModule rewrite_module modules/mod_rewrite.so`
3. Remove the `#` to uncomment it
4. Find `AllowOverride None` and change to `AllowOverride All`
5. Restart Apache

### Step 2: Start the AI Server
1. Open Command Prompt
2. Navigate to: `cd C:\xampp\htdocs\binocularai`
3. Run: `python ai_server.py`
4. Verify it shows: "🚀 Binocular Vision AI Server Starting..."

### Step 3: Test the Android App
1. Run the app on your device/emulator
2. Start any test (Fixation Test, Quick Screening, or Full Assessment)
3. Complete the test
4. Verify:
   - Data is saved to database
   - Screen navigates to AI Analysis
   - Screen navigates to Results
   - Results are displayed correctly

### Step 4: Check Database
Open phpMyAdmin and verify:
- `tests` table has new records with status = 'completed'
- `eye_data` table has eye tracking samples
- `results` table has AI analysis results

## Common Issues & Solutions

### Issue: "Failed to connect to AI server"
**Solution**: Make sure Flask AI server is running on port 5000

### Issue: ".htaccess not working"
**Solution**: 
1. Check if mod_rewrite is enabled in Apache
2. Check if AllowOverride is set to All
3. Restart Apache

### Issue: "Test not saving to database"
**Solution**: 
1. Check database connection in `db.php`
2. Verify database exists and tables are created
3. Check PHP error logs in `C:\xampp\php\logs\php_error_log`

### Issue: "Screen stuck on Saving Data"
**Solution**:
1. Check browser console for API errors
2. Verify Flask server is running
3. Check that test_id is being passed correctly
4. Look at Android Logcat for errors

## API Endpoints Reference

### Start Test
- **Endpoint**: `POST /api/test/start`
- **Request**: `{"user_id": "1", "test_type": "VRG"}`
- **Response**: `{"status": true, "testId": 123, "duration": 120, "message": "Test started"}`

### Submit Eye Data
- **Endpoint**: `POST /api/eye-data`
- **Request**: `{"test_id": 123, "n": 0, "x": 0.5, "y": 0.5, "lx": 0.48, "ly": 0.5, "rx": 0.52, "ry": 0.5}`
- **Response**: `{"status": true, "message": "Eye data sample saved"}`

### Run Analysis (VRG example)
- **Endpoint**: `POST /api/test/vrg`
- **Request**: `{"test_id": 123}`
- **Response**: `{"test_type": "VRG", "score": 0.75, "severity": "Normal", "description": "Your binocular coordination is healthy."}`

## Database Schema

### tests table
- `id` - Auto increment primary key
- `user_id` - Foreign key to users table
- `test_type` - ENUM('RAN', 'VRG', 'PUR')
- `started_at` - DateTime when test started
- `status` - VARCHAR (running/completed)
- `total_samples` - INT count of eye data samples

### eye_data table
- `id` - Auto increment primary key
- `test_id` - Foreign key to tests table
- `n` - Sample number
- `x, y` - Gaze position
- `lx, ly` - Left eye position
- `rx, ry` - Right eye position
- `timestamp` - When sample was recorded

### results table
- `id` - Auto increment primary key
- `test_id` - Foreign key to tests table
- `classification` - VARCHAR (Normal/Mild Issue/Needs Attention)
- `score` - DOUBLE (0.0 to 1.0)
- `ai_notes` - TEXT
- `created_at` - Timestamp
