#!/usr/bin/env pwsh
<#
🚀 GEMINI PRO AUTOMATION PLATFORM - COMPLETE INSTALLER
Run as Administrator!
#>

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🚀 GEMINI PRO AUTOMATION PLATFORM - INSTALLER              ║" -ForegroundColor Cyan
Write-Host "║          Powered by Google Gemini 3.1 Pro                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Check if running as Administrator
$isAdmin = [Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains 'S-1-5-32-544'
if (-not $isAdmin) {
    Write-Host "❌ ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ Running as Administrator`n" -ForegroundColor Green

# ============================================================
# STEP 1: SETUP PROJECT STRUCTURE
# ============================================================

Write-Host "📁 Step 1: Creating project structure..." -ForegroundColor Cyan

$baseDir = "C:\Gemini-AI-Company"
$folders = @(
    "$baseDir",
    "$baseDir\backend",
    "$baseDir\frontend",
    "$baseDir\local-agents",
    "$baseDir\logs",
    "$baseDir\data",
    "$baseDir\docker",
    "$baseDir\config"
)

foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "  ✅ Created: $folder" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️  Exists: $folder" -ForegroundColor Blue
    }
}

# ============================================================
# STEP 2: CREATE ENVIRONMENT FILE
# ============================================================

Write-Host "`n🔐 Step 2: Creating .env file..." -ForegroundColor Cyan

$envFile = "$baseDir\.env"

if (Test-Path $envFile) {
    Write-Host "  ℹ️  .env already exists, skipping..." -ForegroundColor Blue
} else {
    @"
GEMINI_API_KEY=REPLACE_WITH_YOUR_KEY
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
STRIPE_KEY=sk_test_xxx
WEBSITE_URL=http://localhost:3000
API_URL=http://localhost:8000
ENVIRONMENT=development
"@ | Out-File -FilePath $envFile -Encoding UTF8 -Force
    Write-Host "  ✅ Created: $envFile" -ForegroundColor Green
}

# ============================================================
# STEP 3: CHECK PYTHON
# ============================================================

Write-Host "`n🐍 Step 3: Checking Python..." -ForegroundColor Cyan

try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Python not found. Installing..." -ForegroundColor Yellow
    # Provide instructions
    Write-Host "  Please download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  Make sure to check 'Add Python to PATH'" -ForegroundColor Yellow
    exit 1
}

# ============================================================
# STEP 4: INSTALL PYTHON DEPENDENCIES
# ============================================================

Write-Host "`n📦 Step 4: Installing Python dependencies..." -ForegroundColor Cyan

Set-Location $baseDir

if (Test-Path "requirements.txt") {
    Write-Host "  Installing from requirements.txt..." -ForegroundColor Blue
    python -m pip install --upgrade pip | Out-Null
    python -m pip install -r requirements.txt -q

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ℹ️  requirements.txt not found, skipping pip install" -ForegroundColor Blue
}

# ============================================================
# STEP 5: CHECK DOCKER (Optional)
# ============================================================

Write-Host "`n🐳 Step 5: Checking Docker..." -ForegroundColor Cyan

try {
    $dockerVersion = docker --version 2>&1
    Write-Host "  ✅ Docker installed: $dockerVersion" -ForegroundColor Green
    Write-Host "  💡 Tip: Run 'docker-compose up' to start all services" -ForegroundColor Blue
} catch {
    Write-Host "  ℹ️  Docker not installed (optional)" -ForegroundColor Blue
    Write-Host "  Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
}

# ============================================================
# STEP 6: CREATE WINDOWS SCHEDULED TASKS
# ============================================================

Write-Host "`n⏰ Step 6: Setting up Windows Task Scheduler..." -ForegroundColor Cyan

# Email Processor Task
Write-Host "  Creating EmailProcessor task..." -ForegroundColor Blue
$emailAction = New-ScheduledTaskAction -Execute "python" `
    -Argument "$baseDir\local-agents\local_agents_complete.py email"

$emailTrigger = New-ScheduledTaskTrigger -AtStartup

# Remove existing task if it exists
try {
    Unregister-ScheduledTask -TaskName "GeminiEmailProcessor" -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

Register-ScheduledTask -Action $emailAction `
    -Trigger $emailTrigger `
    -TaskName "GeminiEmailProcessor" `
    -Description "Gemini Pro Email Automation - Runs every 5 minutes" `
    -Force | Out-Null

Write-Host "  ✅ EmailProcessor task created" -ForegroundColor Green

# Lead Generator Task
Write-Host "  Creating LeadGenerator task..." -ForegroundColor Blue
$leadAction = New-ScheduledTaskAction -Execute "python" `
    -Argument "$baseDir\local-agents\local_agents_complete.py leads"

$leadTrigger = New-ScheduledTaskTrigger -AtStartup

try {
    Unregister-ScheduledTask -TaskName "GeminiLeadGenerator" -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

Register-ScheduledTask -Action $leadAction `
    -Trigger $leadTrigger `
    -TaskName "GeminiLeadGenerator" `
    -Description "Gemini Pro Lead Generation - Runs every 30 minutes" `
    -Force | Out-Null

Write-Host "  ✅ LeadGenerator task created" -ForegroundColor Green

# Website Monitor Task
Write-Host "  Creating WebsiteMonitor task..." -ForegroundColor Blue
$monitorAction = New-ScheduledTaskAction -Execute "python" `
    -Argument "$baseDir\local-agents\local_agents_complete.py monitor"

$monitorTrigger = New-ScheduledTaskTrigger -AtStartup

try {
    Unregister-ScheduledTask -TaskName "GeminiWebsiteMonitor" -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

Register-ScheduledTask -Action $monitorAction `
    -Trigger $monitorTrigger `
    -TaskName "GeminiWebsiteMonitor" `
    -Description "Gemini Pro Website Monitoring - Runs every 5 minutes" `
    -Force | Out-Null

Write-Host "  ✅ WebsiteMonitor task created" -ForegroundColor Green

# ============================================================
# STEP 7: START SERVICES
# ============================================================

Write-Host "`n🚀 Step 7: Starting services..." -ForegroundColor Cyan

# Start Backend API
Write-Host "  Starting Backend API (port 8000)..." -ForegroundColor Blue
Start-Process -FilePath "python" -ArgumentList "$baseDir\backend_main.py" -WorkingDirectory $baseDir -NoNewWindow

Write-Host "  ✅ Backend API starting (http://localhost:8000)" -ForegroundColor Green

# Start Local Agents
Write-Host "  Starting Local Agents..." -ForegroundColor Blue
Start-Process -FilePath "python" -ArgumentList "$baseDir\local-agents\local_agents_complete.py" -WorkingDirectory "$baseDir\local-agents" -NoNewWindow

Write-Host "  ✅ Local Agents started" -ForegroundColor Green

# ============================================================
# FINAL SUMMARY
# ============================================================

Write-Host "`n" -ForegroundColor Green
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  ✅ SETUP COMPLETE!                            ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📋 NEXT STEPS:" -ForegroundColor Cyan

Write-Host "`n1. CONFIGURE API KEYS:" -ForegroundColor Yellow
Write-Host "   • Edit: $baseDir\.env" -ForegroundColor Gray
Write-Host "   • Add your Gemini Pro API key" -ForegroundColor Gray
Write-Host "   • Add Supabase credentials" -ForegroundColor Gray
Write-Host "   • Add Stripe keys" -ForegroundColor Gray

Write-Host "`n2. START BACKEND API:" -ForegroundColor Yellow
Write-Host "   cd $baseDir" -ForegroundColor Gray
Write-Host "   python backend_main.py" -ForegroundColor Gray
Write-Host "   • Visit: http://localhost:8000/docs" -ForegroundColor Gray

Write-Host "`n3. START FRONTEND:" -ForegroundColor Yellow
Write-Host "   cd $baseDir\frontend" -ForegroundColor Gray
Write-Host "   npm install && npm run dev" -ForegroundColor Gray
Write-Host "   • Visit: http://localhost:3000" -ForegroundColor Gray

Write-Host "`n4. LOCAL AGENTS (24/7 Running):" -ForegroundColor Yellow
Write-Host "   • EmailProcessor: Every 5 minutes" -ForegroundColor Gray
Write-Host "   • LeadGenerator: Every 30 minutes" -ForegroundColor Gray
Write-Host "   • WebsiteMonitor: Every 5 minutes" -ForegroundColor Gray
Write-Host "   • Check logs: $baseDir\logs\" -ForegroundColor Gray

Write-Host "`n5. DOCKER (Optional):" -ForegroundColor Yellow
Write-Host "   docker-compose up -d" -ForegroundColor Gray
Write-Host "   • All services will start automatically" -ForegroundColor Gray

Write-Host "`n📊 MONITORING:" -ForegroundColor Cyan
Write-Host "   • Dashboard: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "   • Logs: $baseDir\logs\agents.log" -ForegroundColor Gray
Write-Host "   • Frontend: http://localhost:3000" -ForegroundColor Gray

Write-Host "`n🎯 TASKS CREATED IN WINDOWS SCHEDULER:" -ForegroundColor Cyan
Write-Host "   • GeminiEmailProcessor" -ForegroundColor Gray
Write-Host "   • GeminiLeadGenerator" -ForegroundColor Gray
Write-Host "   • GeminiWebsiteMonitor" -ForegroundColor Gray
Write-Host "   (Check Task Scheduler if you want to modify timing)" -ForegroundColor Gray

Write-Host "`n💡 TIPS:" -ForegroundColor Blue
Write-Host "   • First API call will download Gemini models (~500MB)" -ForegroundColor Gray
Write-Host "   • Local agents run 24/7 even when desktop is idle" -ForegroundColor Gray
Write-Host "   • Check logs for any errors or issues" -ForegroundColor Gray
Write-Host "   • Use Gemini Studio to test API: https://ai.google.dev/studio" -ForegroundColor Gray

Write-Host "`n🔗 USEFUL LINKS:" -ForegroundColor Blue
Write-Host "   • Gemini API Docs: https://ai.google.dev/docs" -ForegroundColor Cyan
Write-Host "   • Supabase: https://supabase.com" -ForegroundColor Cyan
Write-Host "   • Stripe: https://stripe.com" -ForegroundColor Cyan
Write-Host "   • Vercel Deploy: https://vercel.com" -ForegroundColor Cyan

Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "Ready to automate? 🚀" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Green
