// ================= FORGOT PASSWORD - FRONTEND EXAMPLES =================

// ============= VANILLA JAVASCRIPT =============

// Function: Send Forgot Password Email
async function sendForgotPasswordEmail(email) {
  try {
    const response = await fetch('http://localhost:5000/forgot-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email: email })
    });

    const data = await response.json();

    if (data.status) {
      console.log('✅ Success:', data.message);
      alert('Check your email for the password reset link');
      return true;
    } else {
      console.log('❌ Error:', data.message);
      alert('Error: ' + data.message);
      return false;
    }
  } catch (error) {
    console.error('Request failed:', error);
    alert('Failed to send reset email. Please try again.');
    return false;
  }
}

// Function: Reset Password with Token
async function resetPassword(token, newPassword) {
  try {
    const response = await fetch(`http://localhost:5000/reset-password/${token}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ password: newPassword })
    });

    const data = await response.json();

    if (data.status) {
      console.log('✅ Success:', data.message);
      alert('Password reset successfully! Redirecting to login...');
      // Redirect to login after 2 seconds
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
      return true;
    } else {
      console.log('❌ Error:', data.message);
      alert('Error: ' + data.message);
      return false;
    }
  } catch (error) {
    console.error('Request failed:', error);
    alert('Failed to reset password. Please try again.');
    return false;
  }
}

// ============= REACT COMPONENT - FORGOT PASSWORD =============

import React, { useState } from 'react';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await fetch('http://localhost:5000/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (data.status) {
        setMessage(data.message);
        setEmail('');
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to send reset email. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2>Forgot Password?</h2>
        <p>Enter your email address and we'll send you a link to reset your password.</p>

        <form onSubmit={handleSubmit}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your-email@example.com"
            required
            disabled={isLoading}
            style={styles.input}
          />

          <button
            type="submit"
            disabled={isLoading}
            style={styles.button}
          >
            {isLoading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        {message && (
          <div style={{ ...styles.message, color: 'green' }}>
            ✅ {message}
          </div>
        )}

        {error && (
          <div style={{ ...styles.message, color: '#d9534f' }}>
            ❌ {error}
          </div>
        )}

        <p style={styles.helpText}>
          Remember your password? <a href="/login">Back to Login</a>
        </p>
      </div>
    </div>
  );
}

// ============= REACT COMPONENT - RESET PASSWORD =============

import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const token = searchParams.get('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password strength
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!passwordRegex.test(password)) {
      setError('Password must be 8+ chars with uppercase, lowercase, digit, and special character (@$!%*?&)');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`http://localhost:5000/reset-password/${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      });

      const data = await response.json();

      if (data.status) {
        setMessage(data.message);
        setPassword('');
        setConfirmPassword('');
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to reset password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2>❌ Invalid Reset Link</h2>
          <p>The password reset link is missing or invalid.</p>
          <a href="/forgot-password" style={styles.link}>Request a new reset link</a>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2>Reset Your Password</h2>
        <p>Enter a new password below.</p>

        <form onSubmit={handleSubmit}>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="New password (8+ chars, mixed case, digit, special)"
            required
            disabled={isLoading}
            style={styles.input}
          />

          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm password"
            required
            disabled={isLoading}
            style={styles.input}
          />

          <PasswordStrengthIndicator password={password} />

          <button
            type="submit"
            disabled={isLoading}
            style={styles.button}
          >
            {isLoading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>

        {message && (
          <div style={{ ...styles.message, color: 'green' }}>
            ✅ {message}
          </div>
        )}

        {error && (
          <div style={{ ...styles.message, color: '#d9534f' }}>
            ❌ {error}
          </div>
        )}
      </div>
    </div>
  );
}

// ============= PASSWORD STRENGTH INDICATOR =============

function PasswordStrengthIndicator({ password }) {
  const getStrength = () => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/@$!%*?&/.test(password)) strength++;
    return strength;
  };

  const strength = getStrength();
  const strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
  const strengthColor = ['#d9534f', '#d58512', '#f0ad4e', '#5bc0de', '#5cb85c', '#28a745'];

  return (
    <div style={{ marginBottom: '15px' }}>
      <div style={{ fontSize: '12px', marginBottom: '5px' }}>
        Strength: <span style={{ color: strengthColor[strength] }}>{strengthText[strength]}</span>
      </div>
      <div style={{
        backgroundColor: '#e9ecef',
        borderRadius: '4px',
        height: '5px',
        overflow: 'hidden'
      }}>
        <div style={{
          backgroundColor: strengthColor[strength],
          height: '100%',
          width: `${(strength / 5) * 100}%`,
          transition: 'width 0.3s'
        }} />
      </div>
      <div style={{ fontSize: '11px', marginTop: '5px', color: '#666' }}>
        ✓ Min 8 characters {password.length >= 8 ? '✓' : ''}
        <br />
        ✓ Uppercase letter {/[A-Z]/.test(password) ? '✓' : ''}
        <br />
        ✓ Lowercase letter {/[a-z]/.test(password) ? '✓' : ''}
        <br />
        ✓ Number {/\d/.test(password) ? '✓' : ''}
        <br />
        ✓ Special character (@$!%*?&) {/@$!%*?&/.test(password) ? '✓' : ''}
      </div>
    </div>
  );
}

// ============= STYLES =============

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    padding: '20px'
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    padding: '40px',
    maxWidth: '400px',
    width: '100%'
  },
  input: {
    width: '100%',
    padding: '12px',
    marginBottom: '15px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    boxSizing: 'border-box'
  },
  button: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginBottom: '15px'
  },
  message: {
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '15px',
    textAlign: 'center'
  },
  helpText: {
    textAlign: 'center',
    fontSize: '14px',
    color: '#666'
  },
  link: {
    color: '#007bff',
    textDecoration: 'none'
  }
};

// ============= USAGE EXAMPLE =============

/*
1. Import component in your main app:
   import { ForgotPasswordPage, ResetPasswordPage } from './components/PasswordReset';

2. Add routes:
   <Route path="/forgot-password" element={<ForgotPasswordPage />} />
   <Route path="/reset-password" element={<ResetPasswordPage />} />

3. Link from login page:
   <a href="/forgot-password">Forgot your password?</a>

4. The reset link email sends user to:
   http://localhost:3000/reset-password?token=XXXXX
*/
