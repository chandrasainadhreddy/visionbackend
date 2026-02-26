-- ================= FORGOT PASSWORD FEATURE =================
-- Add these columns to the users table to support password reset

ALTER TABLE users ADD COLUMN reset_token VARCHAR(255) DEFAULT NULL;
ALTER TABLE users ADD COLUMN reset_token_expiry DATETIME DEFAULT NULL;

-- Add index for faster token lookups
CREATE INDEX idx_reset_token ON users(reset_token);

-- ================= MIGRATION COMPLETE =================
-- Users table now supports:
-- - reset_token: Secure token generated for password reset
-- - reset_token_expiry: Expiration time for the reset token (30 minutes)
