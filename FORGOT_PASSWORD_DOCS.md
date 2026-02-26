# Forgot Password Feature Documentation

## Overview
Complete forgot password implementation with secure token-based password reset via email.

## Features Implemented
- ✅ Secure token generation (URL-safe, 32-byte tokens)
- ✅ 30-minute token expiration
- ✅ Email validation
- ✅ Password strength requirements
- ✅ HTML email templates
- ✅ Confirmation emails
- ✅ Security best practices (don't reveal if email exists)
- ✅ Flask-Mail integration
- ✅ Bcrypt password hashing

## Database Changes

### SQL Migration
Run this command in MySQL to add required columns:

```sql
ALTER TABLE users ADD COLUMN reset_token VARCHAR(255) DEFAULT NULL;
ALTER TABLE users ADD COLUMN reset_token_expiry DATETIME DEFAULT NULL;
CREATE INDEX idx_reset_token ON users(reset_token);
```

Or use the included `DATABASE_MIGRATIONS.sql` file.

## Installation

### 1. Install Dependencies
```bash
pip install Flask-Mail
pip install python-dotenv  # For environment variables
```

### 2. Configuration
Create a `.env` file in the project root:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=noreply@binocularai.com
```

### 3. Gmail Setup (if using Gmail)
1. Enable 2-Factor Authentication on Google Account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Copy the 16-character app password
5. Paste into `.env` file

### 4. Update app.py
The code is already integrated. Just set environment variables.

## API Endpoints

### POST /forgot-password
Request user's password reset email.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (Success):**
```json
{
  "status": true,
  "message": "If account exists, password reset link sent to email"
}
```

**Note:** Always returns success to prevent email enumeration attacks.

**Status Codes:**
- `200` - Email sent (if account exists)
- `400` - Invalid email format
- `500` - Server error

---

### POST /reset-password/<token>
Reset password with valid token.

**URL Parameters:**
- `token` - Reset token from email link

**Request:**
```json
{
  "password": "NewPassword123!"
}
```

**Response (Success):**
```json
{
  "status": true,
  "message": "Password reset successfully. Please log in."
}
```

**Response (Invalid Token):**
```json
{
  "status": false,
  "message": "Invalid or expired reset token"
}
```

**Response (Weak Password):**
```json
{
  "status": false,
  "message": "Password must be 8+ chars with uppercase, lowercase, digit, and special character"
}
```

**Status Codes:**
- `200` - Password reset successfully
- `400` - Invalid/expired token or weak password
- `500` - Server error

## Password Requirements
- **Minimum length:** 8 characters
- **Must contain:**
  - At least 1 uppercase letter (A-Z)
  - At least 1 lowercase letter (a-z)
  - At least 1 digit (0-9)
  - At least 1 special character (@$!%*?&)

**Examples:**
- ✅ `MyPass123!`
- ✅ `Secure@Pass456`
- ❌ `password123` (no uppercase or special char)
- ❌ `Pass123` (special char missing)

## Frontend Integration Example

### React Component (forgot-password)
```javascript
import { useState } from 'react';

export function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:5000/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const data = await response.json();
      if (data.status) {
        setMessage('Check your email for reset link');
        setEmail('');
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to send reset email');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        required
      />
      <button type="submit">Send Reset Link</button>
      {message && <p style={{color: 'green'}}>{message}</p>}
      {error && <p style={{color: 'red'}}>{error}</p>}
    </form>
  );
}
```

### React Component (reset-password)
```javascript
import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';

export function ResetPassword() {
  const [searchParams] = useSearchParams();
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const token = searchParams.get('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`http://localhost:5000/reset-password/${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      });
      const data = await response.json();
      if (data.status) {
        setMessage('Password reset successfully! Redirecting to login...');
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to reset password');
    }
  };

  if (!token) {
    return <div>Invalid or missing reset token</div>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="New password (8+ chars, uppercase, lowercase, digit, special)"
        required
      />
      <button type="submit">Reset Password</button>
      {message && <p style={{color: 'green'}}>{message}</p>}
      {error && <p style={{color: 'red'}}>{error}</p>}
    </form>
  );
}
```

## Security Features

### 1. Token Security
- **32-byte random tokens** generated with `secrets.token_urlsafe()`
- **30-minute expiration** - tokens expire after 30 minutes
- **Single-use tokens** - tokens are cleared after successful reset
- **Database lookup** - tokens verified against stored hash

### 2. Password Security
- **Bcrypt hashing** with salt (same as registration/login)
- **Strength validation** - enforced via regex before hashing
- **Never stored in plaintext** - always hashed

### 3. User Privacy
- **Email enumeration prevention** - always returns success message
- **No sensitive data in error messages** - vague token error messages
- **Confirmation emails** - user notified of password changes

### 4. Rate Limiting (Optional - Recommended for Production)
Consider adding rate limiting to prevent brute force attempts:

```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route("/forgot-password", methods=["POST"])
@limiter.limit("5 per hour")
def forgot_password():
    # ... route code
```

## Testing

### Test Forgot Password Flow
```bash
curl -X POST http://localhost:5000/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Test Reset Password
```bash
curl -X POST http://localhost:5000/reset-password/YOUR_TOKEN_HERE \
  -H "Content-Type: application/json" \
  -d '{"password": "NewPassword123!"}'
```

## Troubleshooting

### Gmail: "Login attempt unsuccessful"
- Enable 2FA on Google Account
- Generate app-specific password (16 chars)
- Use app password, NOT your regular Gmail password
- Check that credentials are correctly in .env

### Email not sending silently
- Check Flask logs for SMTP errors
- Verify MAIL_USERNAME and MAIL_PASSWORD
- Ensure firewall allows port 587 (SMTP)
- Check Gmail spam folder

### Token validation fails
- Token may have expired (30-minute limit)
- Token may have already been used (cleared after reset)
- Check database field types (VARCHAR, DATETIME)

### Password validation fails
- Must be 8+ characters
- Must have uppercase AND lowercase
- Must have digit AND special character
- Allowed special chars: @$!%*?&

## Environment-Specific Configuration

### Development (localhost)
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=dev-email@gmail.com
MAIL_PASSWORD=dev-app-password
MAIL_DEFAULT_SENDER=dev@example.com
```

### Production (Domain)
```
MAIL_SERVER=your-domain-smtp.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=noreply@yourdomain.com
MAIL_PASSWORD=production-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

Reset link URL should also be updated:
```python
reset_link = f"https://yourdomain.com/reset-password?token={reset_token}"
```

## Files Modified/Created

1. **app.py** - Added 2 new routes + Flask-Mail config
2. **DATABASE_MIGRATIONS.sql** - Database schema changes
3. **.env.example** - Configuration template
4. **This documentation file**

## Next Steps

1. ✅ Run database migration
2. ✅ Install Flask-Mail and python-dotenv
3. ✅ Configure .env file with email credentials
4. ✅ Test endpoints with cURL or Postman
5. ✅ Integrate frontend components
6. ✅ Add rate limiting for production
7. ✅ Update reset link domain for production
8. ✅ Consider adding email verification feature

## Support

For issues with:
- **Flask-Mail:** Check official docs: https://flask-mail.readthedocs.io/
- **Bcrypt:** See Flask-Bcrypt docs: https://flask-bcrypt.readthedocs.io/
- **Gmail:** Generate app password: https://myaccount.google.com/apppasswords
