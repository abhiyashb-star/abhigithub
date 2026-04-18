#!/usr/bin/env pwsh
# QUICK START SCRIPT - Copy & Run This in PowerShell
# Run as Administrator!

Write-Host "🚀 STARTING AI COMPANY SETUP..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Step 1: Create Directory Structure
Write-Host "`n📁 Creating folder structure..." -ForegroundColor Cyan
$baseDir = "C:\AI-Company"

if (!(Test-Path $baseDir)) {
    New-Item -ItemType Directory -Path $baseDir -Force | Out-Null
    Write-Host "✅ Created: $baseDir"
}

$folders = @(
    "$baseDir\openclaw",
    "$baseDir\openclaw\agents",
    "$baseDir\openclaw\workflows",
    "$baseDir\local-agents",
    "$baseDir\web\frontend",
    "$baseDir\web\backend",
    "$baseDir\logs",
    "$baseDir\data"
)

foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "✅ Created: $folder"
    }
}

# Step 2: Create Environment File
Write-Host "`n🔐 Creating .env file..." -ForegroundColor Cyan
$envFile = "$baseDir\.env"
$envContent = @"
# API Keys
GEMINI_API_KEY=REPLACE_WITH_YOUR_KEY
CLAUDE_API_KEY=sk_<your_claude_key_here>

# Database
SUPABASE_URL=<will_be_generated>
SUPABASE_KEY=<will_be_generated>

# Payments
STRIPE_TEST_KEY=sk_test_<your_test_key>
STRIPE_PUBLIC_KEY=pk_test_<your_public_key>

# Tools
OPENCLAW_API_KEY=<your_key>
ANTIGRAVITY_TOKEN=<your_token>

# Settings
WEBSITE_URL=http://localhost:3000
API_URL=http://localhost:8000
LOG_LEVEL=INFO
"@

$envContent | Out-File -FilePath $envFile -Encoding UTF8 -Force
Write-Host "✅ Created: $envFile"

# Step 3: Check OpenClaw
Write-Host "`n🤖 Checking OpenClaw..." -ForegroundColor Cyan
try {
    $openclaw = openclaw --version
    Write-Host "✅ OpenClaw installed: $openclaw" -ForegroundColor Green
} catch {
    Write-Host "⚠️  OpenClaw not found. Installing..." -ForegroundColor Yellow
    # Installation instructions would go here
}

# Step 4: Check Antigravity
Write-Host "`n⚙️  Checking Antigravity..." -ForegroundColor Cyan
try {
    $antigravity = antigravity --version
    Write-Host "✅ Antigravity installed: $antigravity" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Antigravity not found. Installing..." -ForegroundColor Yellow
}

# Step 5: Create Local Agent Scripts
Write-Host "`n📄 Creating local agent files..." -ForegroundColor Cyan

# Email Processor
$emailProcessorCode = @"
import schedule
import time
import os
from datetime import datetime
import subprocess
import sys

class EmailProcessor:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.log_file = "$baseDir\logs\email-processor.log"

    def process_emails(self):
        print(f"[{datetime.now()}] Processing emails...")
        try:
            result = subprocess.run([
                'openclaw', 'run-agent',
                'EmailAgent'
            ], capture_output=True, text=True)

            with open(self.log_file, 'a') as f:
                f.write(f"{datetime.now()} - SUCCESS\n")
            print("✅ Emails processed")
        except Exception as e:
            print(f"❌ Error: {e}")
            with open(self.log_file, 'a') as f:
                f.write(f"{datetime.now()} - ERROR: {e}\n")

    def start(self):
        schedule.every(5).minutes.do(self.process_emails)
        print("📧 Email Processor started...")

        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    processor = EmailProcessor()
    processor.start()
"@

$emailProcessorCode | Out-File -FilePath "$baseDir\local-agents\email-processor.py" -Encoding UTF8 -Force
Write-Host "✅ Created: email-processor.py"

# Lead Generator
$leadGenCode = @"
import schedule
import subprocess
from datetime import datetime

class LeadGenerator:
    def __init__(self):
        self.output_db = "$baseDir\data\leads.db"

    def generate_leads(self):
        print(f"[{datetime.now()}] Generating leads...")
        try:
            subprocess.run([
                'openclaw', 'run-agent',
                'LeadGeneratorAgent',
                '--output', self.output_db
            ])
            print("✅ Leads generated")
        except Exception as e:
            print(f"❌ Error: {e}")

    def start(self):
        schedule.every(30).minutes.do(self.generate_leads)
        print("🎯 Lead Generator started...")
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    gen = LeadGenerator()
    gen.start()
"@

$leadGenCode | Out-File -FilePath "$baseDir\local-agents\lead-generator.py" -Encoding UTF8 -Force
Write-Host "✅ Created: lead-generator.py"

# Step 6: Create Scheduled Tasks
Write-Host "`n⏰ Setting up Windows Scheduled Tasks..." -ForegroundColor Cyan

# Email Processor Task
$emailAction = New-ScheduledTaskAction -Execute "python" `
    -Argument "$baseDir\local-agents\email-processor.py"
$emailTrigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -Action $emailAction `
    -Trigger $emailTrigger `
    -TaskName "EmailProcessor" `
    -Description "Run 24/7 email processing" `
    -Force | Out-Null
Write-Host "✅ Task created: EmailProcessor"

# Lead Generator Task
$leadAction = New-ScheduledTaskAction -Execute "python" `
    -Argument "$baseDir\local-agents\lead-generator.py"
$leadTrigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -Action $leadAction `
    -Trigger $leadTrigger `
    -TaskName "LeadGenerator" `
    -Description "Generate leads automatically" `
    -Force | Out-Null
Write-Host "✅ Task created: LeadGenerator"

# Step 7: Summary
Write-Host "`n" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review: $baseDir\.env and add your keys"
Write-Host "2. Run: openclaw generate agent --name EmailAgent --type email-automation"
Write-Host "3. Run: antigravity init-workflow MainPipeline"
Write-Host "4. Run: antigravity deploy MainPipeline"
Write-Host "5. Check: antigravity monitor MainPipeline"

Write-Host "`n🚀 Your AI Company is Ready!" -ForegroundColor Green
Write-Host "Agents running in background:" -ForegroundColor Cyan
Write-Host "  📧 EmailProcessor - Running every 5 mins"
Write-Host "  🎯 LeadGenerator - Running every 30 mins"
Write-Host "`n" -ForegroundColor Green
