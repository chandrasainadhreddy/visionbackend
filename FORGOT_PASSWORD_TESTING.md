# Forgot Password Feature - Testing Guide

## Quick Test Steps

### 1. Setup
```bash
# Install dependencies
pip install Flask-Mail python-dotenv

# Create .env file from template
copy .env.example .env

# Edit .env with your email credentials
```

### 2. Database
```sql
-- Run in MySQL
ALTER TABLE users ADD COLUMN reset_token VARCHAR(255) DEFAULT NULL;
ALTER TABLE users ADD COLUMN reset_token_expiry DATETIME DEFAULT NULL;
CREATE INDEX idx_reset_token ON users(reset_token);
```

### 3. Start Flask Server
```bash
python app.py
```

### 4. Test Forgot Password Endpoint

Using cURL:
```bash
curl -X POST http://localhost:5000/forgot-password \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"yourtest@example.com\"}"
```

Expected response:
```json
{
  "status": true,
  "message": "If account exists, password reset link sent to email"
}
```

### 5. Check Email
Check your inbox for the reset email. The link will look like:
```
http://localhost:3000/reset-password?token=XXXXXXXXXXXXXXXXXXXXX
```

### 6. Test Reset Password Endpoint

Using cURL:
```bash
curl -X POST http://localhost:5000/reset-password/YOUR_TOKEN_HERE \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"NewPassword123!\"}"
```

Replace `YOUR_TOKEN_HERE` with the token from the email.

Expected response (success):
```json
{
  "status": true,
  "message": "Password reset successfully. Please log in."
}
```

Expected response (invalid token):
```json
{
  "status": false,
  "message": "Invalid or expired reset token"
}
```

### 7. Login with New Password
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"yourtest@example.com\", \"password\": \"NewPassword123!\"}"
```

Should return user_id if successful.

---

## Test Cases

### Test Case 1: Valid Forgot Password
- **Input:** Valid registered email
- **Expected:** Success message returned
- **Email:** Should receive reset link
- **Result:** ✓ PASS / ✗ FAIL

### Test Case 2: Invalid Email Format
- **Input:** `invalid-email`
- **Expected:** Error message about invalid format
- **Status Code:** 400
- **Result:** ✓ PASS / ✗ FAIL

### Test Case 3: Non-existent Email
- **Input:** Valid format but not registered
- **Expected:** Success message (privacy)
- **Email:** Should NOT receive anything
- **Result:** ✓ PASS / ✗ FAIL

### Test Case 4: Valid Token Reset
- **Input:** Token from email + valid password
- **Expected:** Success message
- **DB Update:** Password hashed and token cleared
- **Result:** ✓ PASS / ✗ FAIL

### Test Case 5: Expired Token Reset
- **Input:** Token older than 30 minutes
- **Expected:** Invalid/expired token error
- **Status Code:** 400
- **Result:** ✓ PASS / ✗ FAIL

### Test Case 6: Invalid Token Format
- **Input:** Random string as token
- **Expected:** Invalid/expired token error
- **Status Code:** 400
- **Result:** ✓ PASS / ✗ FAIL

### Test Case 7: Weak Password
- **Input:** Password without uppercase
- **Expected:** Strength validation error
- **Status Code:** 400
- **Result:** ✓ PASS / ✗ FAIL

### Test Case 8: Strong Password Success
- **Input:** `SecurePass123!`
- **Expected:** Success message
- **Login:** Should work with new password
- **Result:** ✓ PASS / ✗ FAIL

### Test Case 9: Token Reuse (already used)
- **Input:** Same token twice
- **Expected:** First succeeds, second fails
- **Result:** ✓ PASS / ✗ FAIL

### Test Case 10: Login with New Password
- **Input:** New credentials from reset
- **Expected:** Returns valid user_id
- **Old Password:** Should NOT work anymore
- **Result:** ✓ PASS / ✗ FAIL

---

## Debugging

### Email Not Sending?
Check Flask console output:
```
❌ Email send failed: [Error details]
```

Common issues:
1. Wrong MAIL_USERNAME or MAIL_PASSWORD
2. Gmail 2FA not enabled
3. Using regular password instead of app password
4. Firewall blocking port 587

### Token Not Validating?
Check database:
```sql
SELECT id, reset_token, reset_token_expiry FROM users WHERE reset_token IS NOT NULL;
```

Should show:
- Token stored in DB
- Expiry time is future timestamp
- Token matches URL

### Password Validation Failing?
Test regex pattern. Password must have:
- ✅ Minimum 8 characters
- ✅ At least 1 uppercase (A-Z)
- ✅ At least 1 lowercase (a-z)
- ✅ At least 1 digit (0-9)
- ✅ At least 1 special character (@$!%*?&)

Valid examples:
- `MyPass123!`
- `Secure@Word456`
- `Test@1234`

Invalid examples:
- `password123` (no uppercase/special)
- `Pass123` (no special)
- `Pass!` (too short)
- `PASSWORD123!` (no lowercase)

---

## API Response Reference

### Success Responses

**Forgot Password - Success**
```json
{
  "status": true,
  "message": "If account exists, password reset link sent to email"
}
```

**Reset Password - Success**
```json
{
  "status": true,
  "message": "Password reset successfully. Please log in."
}
```

### Error Responses

**Invalid Email Format**
```json
{
  "status": false,
  "message": "Invalid email format"
}
```

**Invalid/Expired Token**
```json
{
  "status": false,
  "message": "Invalid or expired reset token"
}
```

**Weak Password**
```json
{
  "status": false,
  "message": "Password must be 8+ chars with uppercase, lowercase, digit, and special character"
}
```

**Server Error**
```json
{
  "status": false,
  "error": "[Error details]"
}
```

---

## Performance Notes

### Database
- Token lookup uses index: `idx_reset_token`
- No N+1 queries
- Single UPDATE per reset

### Email
- Async sending recommended for production
- Current implementation blocks briefly
- Consider Celery/Redis for high volume

### Token Generation
- 32-byte URL-safe tokens = 256 bits entropy
- Collision probability: essentially zero
- Good for both security and UX
