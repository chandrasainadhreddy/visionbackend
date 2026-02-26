#!/bin/bash
# ================= FORGOT PASSWORD FEATURE - QUICK START =================
# This script will set up the forgot password feature in 3 commands

echo "===================================================="
echo "  FORGOT PASSWORD FEATURE - QUICK START SETUP"
echo "===================================================="
echo ""

# Step 1: Install dependencies
echo "Step 1: Installing Python packages..."
pip install Flask-Mail python-dotenv
echo "✅ Dependencies installed"
echo ""

# Step 2: Database migration
echo "Step 2: Database migration instructions..."
echo "📋 Run this SQL in your MySQL database:"
echo ""
echo "ALTER TABLE users ADD COLUMN reset_token VARCHAR(255) DEFAULT NULL;"
echo "ALTER TABLE users ADD COLUMN reset_token_expiry DATETIME DEFAULT NULL;"
echo "CREATE INDEX idx_reset_token ON users(reset_token);"
echo ""
echo "⚠️  Press Enter when done with database migration..."
read
echo ""

# Step 3: Configuration
echo "Step 3: Setting up configuration..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    echo "✅ Using existing .env file"
else
    cp .env.example .env
    echo "✅ Created .env from template"
    echo ""
    echo "📝 Edit .env with your email credentials:"
    echo "   - MAIL_USERNAME: your-email@gmail.com"
    echo "   - MAIL_PASSWORD: your-16-char-app-password"
    echo ""
    echo "   For Gmail: https://myaccount.google.com/apppasswords"
fi
echo ""

# Step 4: Verification
echo "Step 4: Verifying setup..."
if [ -f "app.py" ] && grep -q "forgot-password" app.py; then
    echo "✅ Backend routes installed"
else
    echo "❌ Backend routes not found!"
fi

if [ -f ".env" ]; then
    echo "✅ Configuration file created"
else
    echo "❌ Configuration file missing!"
fi

echo ""
echo "===================================================="
echo "  SETUP COMPLETE! 🎉"
echo "===================================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your email credentials"
echo "2. Restart your Flask server: python app.py"
echo "3. Test the feature: see QUICK_REFERENCE_CARD.md"
echo ""
echo "Documentation:"
echo "  - Full API docs: FORGOT_PASSWORD_DOCS.md"
echo "  - Testing guide: FORGOT_PASSWORD_TESTING.md"
echo "  - Quick reference: QUICK_REFERENCE_CARD.md"
echo "  - Frontend code: FORGOT_PASSWORD_FRONTEND_EXAMPLES.js"
echo ""
echo "===================================================="
