# Forgot Password Feature - Quick Reference Card

## 📋 Checklist Before Going Live

- [ ] Install Flask-Mail: `pip install Flask-Mail python-dotenv`
- [ ] Create `.env` file from `.env.example`
- [ ] Configure email credentials (Gmail, SendGrid, etc.)
- [ ] Run database migration SQL
- [ ] Test forgot password with real email account
- [ ] Test reset password with valid token
- [ ] Verify confirmation emails are sent
- [ ] Update reset link domain for production
- [ ] Add rate limiting for production
- [ ] Set environment variables in hosting platform

## 🔌 API Quick Reference

### Forgot Password
```
POST /forgot-password
Content-Type: application/json

Request:
{
  "email": "user@example.com"
}

Response:
{
  "status": true,
  "message": "If account exists, password reset link sent to email"
}
```

### Reset Password
```
POST /reset-password/<token>
Content-Type: application/json

Request:
{
  "password": "NewPassword123!"
}

Response:
{
  "status": true,
  "message": "Password reset successfully. Please log in."
}
```

## 🔐 Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 lowercase letter (a-z)
- At least 1 digit (0-9)
- At least 1 special character (@$!%*?&)

### ✅ Valid Passwords
- `MyPassword123!`
- `Secure@Pass456`
- `Test@1234`

### ❌ Invalid Passwords
- `password123` (no uppercase/special)
- `Pass123` (no special character)
- `Pass!` (too short)
- `PASSWORD123!` (no lowercase)

## 📧 Email Configuration

### Gmail (Recommended for Testing)
1. Enable 2FA: https://myaccount.google.com/
2. Generate app password: https://myaccount.google.com/apppasswords
3. Use 16-character password in `.env`

### .env Template
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=noreply@binocularai.com
```

## 🗄️ Database

### Required Columns
```sql
ALTER TABLE users ADD COLUMN reset_token VARCHAR(255) DEFAULT NULL;
ALTER TABLE users ADD COLUMN reset_token_expiry DATETIME DEFAULT NULL;
CREATE INDEX idx_reset_token ON users(reset_token);
```

### Column Validation
```sql
-- Check columns exist
DESC users;

-- Check if any reset tokens are active
SELECT id, email, reset_token_expiry FROM users WHERE reset_token IS NOT NULL;
```

## 🧪 Quick Test Commands

### Test 1: Send Forgot Password Email
```bash
curl -X POST http://localhost:5000/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### Test 2: Reset with Token
```bash
curl -X POST http://localhost:5000/reset-password/YOUR_TOKEN \
  -H "Content-Type: application/json" \
  -d '{"password": "NewPass123!"}'
```

### Test 3: Login with New Password
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "NewPass123!"}'
```

## 🐛 Troubleshooting

### Email Not Sending
**Problem:** Flask prints "❌ Email send failed"
**Solution:**
1. Check MAIL_USERNAME and MAIL_PASSWORD in .env
2. Verify 2FA enabled on Gmail
3. Use app-specific password (16 chars), not Gmail password
4. Check firewall allows port 587

### Token Invalid Error
**Problem:** "Invalid or expired reset token"
**Solution:**
1. Token expires after 30 minutes
2. Token is single-use (can't reuse)
3. Request new token from forgot-password endpoint

### Password Validation Fails
**Problem:** "Password must be 8+ chars..."
**Solution:**
1. Ensure password is 8+ characters
2. Include uppercase (A-Z)
3. Include lowercase (a-z)
4. Include digit (0-9)
5. Include special character (@$!%*?&)

### Email in .env Not Being Read
**Problem:** App using default values
**Solution:**
1. Rename `.env.example` to `.env`
2. Fill in values (no quotes needed)
3. Restart Flask app
4. Check `app.config['MAIL_USERNAME']` should print your email

## 🔒 Security Checklist

- [ ] Never commit `.env` file
- [ ] Add `.env` to `.gitignore`
- [ ] Use app-specific password, not user password
- [ ] Token expires in 30 minutes
- [ ] Tokens are single-use
- [ ] Passwords hashed with bcrypt
- [ ] Email enumeration prevented
- [ ] Input validation on email and password
- [ ] Rate limiting added for production

## 📊 Database Queries

### Find Active Reset Tokens
```sql
SELECT id, email, reset_token, reset_token_expiry 
FROM users 
WHERE reset_token IS NOT NULL 
AND reset_token_expiry > NOW();
```

### Clear All Reset Tokens
```sql
UPDATE users 
SET reset_token = NULL, reset_token_expiry = NULL 
WHERE reset_token IS NOT NULL;
```

### Check User Password History
```sql
SELECT id, email, password, reset_token_expiry 
FROM users 
WHERE email = 'user@example.com';
```

## 🚀 Common Configuration Changes

### Change Token Expiry Time
**File:** `app.py`
**Line:** In `forgot_password()` function
**Change:**
```python
# Current: 30 minutes
expiry_time = datetime.now() + timedelta(minutes=30)

# To 1 hour:
expiry_time = datetime.now() + timedelta(hours=1)

# To 24 hours:
expiry_time = datetime.now() + timedelta(days=1)
```

### Change Reset Link Domain
**File:** `app.py`
**Line:** In `forgot_password()` function
**Change:**
```python
# Current: localhost
reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

# To production domain:
reset_link = f"https://yourdomain.com/reset-password?token={reset_token}"
```

### Change Password Requirements
**File:** `app.py`
**Line:** In `reset_password()` function
**Pattern:** `password_regex`
```python
# Current pattern (strict)
password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

# Simpler (just 8+ chars):
password_regex = r'^.{8,}$'
```

## 📞 Support Resources

- Flask-Mail Docs: https://flask-mail.readthedocs.io/
- Flask-Bcrypt Docs: https://flask-bcrypt.readthedocs.io/
- Gmail App Passwords: https://myaccount.google.com/apppasswords
- OWASP Password Security: https://cheatsheetseries.owasp.org/

## 📄 Related Files

- `FORGOT_PASSWORD_DOCS.md` - Full documentation
- `FORGOT_PASSWORD_TESTING.md` - Testing guide
- `FORGOT_PASSWORD_FRONTEND_EXAMPLES.js` - React/JS examples
- `DATABASE_MIGRATIONS.sql` - SQL schema
- `.env.example` - Configuration template
- `setup_forgot_password.bat` - Auto setup script
- `IMPLEMENTATION_SUMMARY.md` - Implementation overview
