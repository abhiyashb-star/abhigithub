"""
🚀 LOCAL AGENTS - Run 24/7 on Windows PC
These agents continuously process tasks without stopping
"""

import schedule
import time
import os
import json
import logging
from datetime import datetime
import subprocess
import requests
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load credentials
load_dotenv()

# ============================================================
# LOGGING SETUP
# ============================================================

log_dir = Path("C:\\AI-Company\\logs")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "agents.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# SUPABASE SETUP
# ============================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase Cloud Connection: ACTIVE")
    except Exception as e:
        logger.error(f"❌ Supabase Connection Failed: {e}")

# ============================================================
# 🔱 100CR SQUAD SCHEDULE (Burst-Logic)
# ============================================================

SCHEDULE = {
    "SCOUT_SQUAD": {"start": 6, "end": 9},    # Lead Generation: 6 AM - 9 AM
    "SALES_SQUAD": {"start": 9, "end": 17},   # Outreach: 9 AM - 5 PM
    "PRODUCER_SQUAD": {"start": 17, "end": 22}, # Content Creation: 5 PM - 10 PM
    "OPS_SQUAD": {"start": 0, "end": 24},     # Monitoring: Always On
}

def is_squad_active(squad_name):
    """Check if the specific squad should be running right now"""
    current_hour = datetime.now().hour
    window = SCHEDULE.get(squad_name)
    if not window: return False
    return window["start"] <= current_hour < window["end"]

CONFIG = {
    "email_check_interval": 5,  # minutes
    "lead_generation_interval": 30,  # minutes
    "website_monitor_interval": 5,  # minutes
    "data_sync_interval": 60,  # minutes
}

# ============================================================
# AGENT 1: EMAIL PROCESSOR (Every 5 minutes)
# ============================================================

class EmailProcessor:
    """Continuously process and automate emails"""

    def __init__(self):
        self.logger = logging.getLogger("EmailProcessor")
        self.processed_count = 0
        self.error_count = 0

    def process_emails(self):
        """Main email processing function - Sales Squad"""
        if not is_squad_active("SALES_SQUAD"):
            self.logger.info("⏳ Sales Squad in standby mode. Waiting for active window (9 AM - 5 PM).")
            return

        try:
            self.logger.info(f"📧 Processing emails... (Total: {self.processed_count})")

            # Call backend API
            response = requests.post(
                f"{API_BASE}/email-agent",
                json={
                    "task_type": "email",
                    "input_data": {
                        "action": "classify_and_organize",
                        "keywords": ["urgent", "review", "action_required"]
                    },
                    "reasoning_level": "medium"
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"✅ Emails processed: {result.get('status')}")
                self.processed_count += 1

                # Log to Cloud
                if supabase:
                    try:
                        supabase.table("agent_logs").insert({
                            "agent": "EmailProcessor",
                            "status": "success",
                            "message": f"Processed {self.processed_count} batches",
                            "timestamp": datetime.now().isoformat()
                        }).execute()
                    except: pass
            else:
                self.error_count += 1
                self.logger.error(f"❌ API error: {response.status_code}")

        except Exception as e:
            self.error_count += 1
            self.logger.error(f"❌ Error processing emails: {str(e)}")

    def start(self):
        """Start email processor"""
        self.logger.info("📧 Email Processor starting (every 5 minutes)...")

        schedule.every(CONFIG["email_check_interval"]).minutes.do(self.process_emails)

        while True:
            schedule.run_pending()
            time.sleep(1)

# ============================================================
# AGENT 2: LEAD GENERATOR (Every 30 minutes)
# ============================================================

class LeadGenerator:
    """Continuously find and qualify leads"""

    def __init__(self):
        self.logger = logging.getLogger("LeadGenerator")
        self.leads_generated = 0

    def generate_leads(self):
        """Generate and qualify leads - Scout Squad"""
        if not is_squad_active("SCOUT_SQUAD"):
            self.logger.info("⏳ Scout Squad in standby mode. Waiting for active window (6 AM - 9 AM).")
            return

        try:
            self.logger.info(f"🎯 Generating leads... (Total: {self.leads_generated})")

            response = requests.post(
                f"{API_BASE}/web-scraper",
                json={
                    "task_type": "web_scrape",
                    "input_data": {
                        "search_terms": ["AI automation", "gemini pro", "automation agency"],
                        "platforms": ["linkedin", "twitter", "reddit"],
                        "extract_emails": True
                    },
                    "reasoning_level": "high"
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"✅ Leads found: {result.get('status')}")
                self.leads_generated += 1

                # Save leads to Cloud
                if supabase:
                    try:
                        supabase.table("leads").insert({
                            "source": result.get("source", "web_scraper"),
                            "data": result,
                            "created_at": datetime.now().isoformat()
                        }).execute()
                        self.logger.info("✅ Lead synced to Cloud")
                    except Exception as e:
                        self.logger.error(f"❌ Cloud Sync Failed: {e}")
            else:
                self.logger.error(f"❌ Lead generation failed: {response.status_code}")

        except Exception as e:
            self.logger.error(f"❌ Error generating leads: {str(e)}")

    def start(self):
        """Start lead generator"""
        self.logger.info("🎯 Lead Generator starting (every 30 minutes)...")

        schedule.every(CONFIG["lead_generation_interval"]).minutes.do(self.generate_leads)

        while True:
            schedule.run_pending()
            time.sleep(1)

# ============================================================
# AGENT 3: WEBSITE MONITOR (Every 5 minutes)
# ============================================================

class WebsiteMonitor:
    """Monitor website uptime and performance"""

    def __init__(self):
        self.logger = logging.getLogger("WebsiteMonitor")
        self.website_url = "https://yourwebsite.com"  # Update this
        self.uptime_percentage = 100.0
        self.checks_total = 0
        self.checks_failed = 0

    def check_website(self):
        """Check website status"""
        try:
            start = time.time()
            response = requests.get(self.website_url, timeout=10)
            response_time = (time.time() - start) * 1000

            self.checks_total += 1

            if response.status_code == 200:
                self.logger.info(f"✅ {self.website_url} UP ({response_time:.0f}ms)")
                with open(log_dir / "website-monitor.log", "a") as f:
                    f.write(f"{datetime.now()} - UP - {response_time:.0f}ms\n")
            else:
                self.checks_failed += 1
                self.logger.warning(f"⚠️ Status {response.status_code}")
                self.send_alert(f"Website returned {response.status_code}")

        except Exception as e:
            self.checks_failed += 1
            self.logger.error(f"❌ Website DOWN: {str(e)}")
            self.send_alert(f"Website is DOWN: {str(e)}")

        # Update uptime percentage
        if self.checks_total > 0:
            self.uptime_percentage = ((self.checks_total - self.checks_failed) / self.checks_total) * 100

    def send_alert(self, error_message):
        """Send Slack/Email alert"""
        try:
            requests.post(
                f"{API_BASE}/email-agent",
                json={
                    "task_type": "email",
                    "input_data": {
                        "to": "you@example.com",
                        "subject": "🚨 Website Alert",
                        "body": f"Website monitoring alert: {error_message}"
                    }
                },
                timeout=10
            )
        except:
            self.logger.error("Failed to send alert")

    def start(self):
        """Start website monitor"""
        self.logger.info(f"🌐 Website Monitor starting (every 5 minutes)...")
        self.logger.info(f"📍 Monitoring: {self.website_url}")

        schedule.every(CONFIG["website_monitor_interval"]).minutes.do(self.check_website)

        while True:
            schedule.run_pending()
            time.sleep(1)

# ============================================================
# AGENT 4: DATA SYNC AGENT (Every 60 minutes)
# ============================================================

class DataSyncAgent:
    """Sync data between systems"""

    def __init__(self):
        self.logger = logging.getLogger("DataSyncAgent")
        self.sync_count = 0

    def sync_data(self):
        """Sync local data with cloud"""
        try:
            self.logger.info(f"🔄 Syncing data... (Total: {self.sync_count})")

            # Send local data to cloud
            local_data_file = log_dir.parent / "local_data.json"

            if local_data_file.exists():
                with open(local_data_file, "r") as f:
                    data = json.load(f)

                response = requests.post(
                    f"{API_BASE}/data-analyst",
                    json={
                        "task_type": "data_analysis",
                        "input_data": {"data": data, "sync": True},
                        "reasoning_level": "medium"
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    self.logger.info("✅ Data synced successfully")
                    self.sync_count += 1
                else:
                    self.logger.error(f"❌ Sync failed: {response.status_code}")
            else:
                self.logger.info("ℹ️ No local data to sync")

        except Exception as e:
            self.logger.error(f"❌ Error syncing data: {str(e)}")

    def start(self):
        """Start data sync agent"""
        self.logger.info("🔄 Data Sync Agent starting (every 60 minutes)...")

        schedule.every(CONFIG["data_sync_interval"]).minutes.do(self.sync_data)

        while True:
            schedule.run_pending()
            time.sleep(1)

# ============================================================
# MASTER CONTROLLER
# ============================================================

class LocalAgentController:
    """Manages all local agents"""

    def __init__(self):
        self.logger = logging.getLogger("Controller")
        self.agents = {
            "email": EmailProcessor(),
            "leads": LeadGenerator(),
            "monitor": WebsiteMonitor(),
            "sync": DataSyncAgent()
        }

    def status_report(self):
        """Print status of all agents"""
        self.logger.info("=" * 60)
        self.logger.info("📊 LOCAL AGENTS STATUS REPORT")
        self.logger.info("=" * 60)
        self.logger.info(f"📧 EmailProcessor: {self.agents['email'].processed_count} batches")
        self.logger.info(f"🎯 LeadGenerator: {self.agents['leads'].leads_generated} leads")
        self.logger.info(f"🌐 WebsiteMonitor: {self.agents['monitor'].uptime_percentage:.1f}% uptime")
        self.logger.info(f"🔄 DataSyncAgent: {self.agents['sync'].sync_count} syncs")
        self.logger.info("=" * 60)

    def run_all_agents(self):
        """Run all agents in parallel"""
        self.logger.info("🚀 Starting all local agents...")

        # Schedule daily status report
        schedule.every().day.at("06:00").do(self.status_report)

        # Start agents
        agents_to_run = [
            ("EmailProcessor", self.agents["email"].start),
            ("LeadGenerator", self.agents["leads"].start),
            ("WebsiteMonitor", self.agents["monitor"].start),
            ("DataSyncAgent", self.agents["sync"].start),
        ]

        # Note: In production, use multiprocessing or asyncio
        # For now, this is a template showing how to structure it
        self.logger.info("✅ All agents configured and ready")
        self.logger.info("Run each agent in a separate Windows Task Scheduler task")

# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    logger.info("🚀 Gemini Pro Local Agents Starting...")
    logger.info(f"⏰ Time: {datetime.now()}")
    logger.info(f"📁 Log directory: {log_dir}")

    # Create controller
    controller = LocalAgentController()

    # Run individual agents based on command line argument
    import sys

    if len(sys.argv) > 1:
        agent_name = sys.argv[1]
        if agent_name in controller.agents:
            logger.info(f"Starting {agent_name} agent...")
            controller.agents[agent_name].start()
        else:
            logger.error(f"Unknown agent: {agent_name}")
    else:
        # Run controller setup
        logger.info("Running in controller mode - configure Windows Task Scheduler tasks")
        controller.run_all_agents()
        controller.status_report()

        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(1)
