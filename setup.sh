#!/bin/bash

# DC Gallery Monitoring System Setup Script
# This script helps you set up the project quickly

echo "🎯 DC Gallery Monitoring System Setup"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from project root
if [ ! -f "README.md" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Function to check command availability
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗ $1 is not installed${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $1 is installed${NC}"
        return 0
    fi
}

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
echo "---------------------------------"

check_command "python3"
PYTHON_OK=$?

check_command "node"
NODE_OK=$?

check_command "npm"
NPM_OK=$?

check_command "git"
GIT_OK=$?

if [ $PYTHON_OK -ne 0 ] || [ $NODE_OK -ne 0 ] || [ $NPM_OK -ne 0 ] || [ $GIT_OK -ne 0 ]; then
    echo -e "${YELLOW}Please install missing prerequisites before continuing${NC}"
    exit 1
fi

echo ""

# Step 2: Python virtual environment
echo "Step 2: Setting up Python environment..."
echo "---------------------------------------"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r crawler/requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Python dependencies installed${NC}"

echo ""

# Step 3: Check for .env file
echo "Step 3: Environment configuration..."
echo "-----------------------------------"

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ .env file created. Please edit it with your API keys${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""

# Step 4: Supabase setup reminder
echo "Step 4: Supabase Setup Checklist"
echo "--------------------------------"
echo "Please ensure you have:"
echo "  [ ] Created a Supabase account at https://supabase.com"
echo "  [ ] Created a new project"
echo "  [ ] Copied your project URL and keys to .env"
echo "  [ ] Run the migration script in supabase/migrations/"
echo ""

# Step 5: GitHub setup reminder
echo "Step 5: GitHub Setup Checklist"
echo "------------------------------"
echo "Please ensure you have:"
echo "  [ ] Created a private GitHub repository"
echo "  [ ] Added the following secrets in Settings > Secrets:"
echo "      - SUPABASE_URL"
echo "      - SUPABASE_SERVICE_KEY"
echo "  [ ] Enabled GitHub Actions"
echo ""

# Step 6: Telegram Bot setup reminder
echo "Step 6: Telegram Bot Setup"
echo "--------------------------"
echo "Please ensure you have:"
echo "  [ ] Created a bot via @BotFather"
echo "  [ ] Copied the bot token to .env"
echo "  [ ] Created a group/channel and added the bot"
echo "  [ ] Obtained the chat ID"
echo ""

# Step 7: Test crawler
echo "Step 7: Testing the crawler..."
echo "-----------------------------"

read -p "Do you want to test the crawler now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running crawler test..."
    python crawler/main.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Crawler test successful!${NC}"
    else
        echo -e "${RED}✗ Crawler test failed. Please check your configuration${NC}"
    fi
fi

echo ""
echo "================================"
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Set up Supabase database with the migration script"
echo "3. Configure GitHub repository and secrets"
echo "4. Push code to GitHub to activate automatic crawling"
echo ""
echo "For more information, check the README.md file"
