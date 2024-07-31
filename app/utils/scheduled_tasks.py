from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from services.htmlparse.service import synchronize_daily_suggestion_data
from utils.middleware import SessionLocal

scheduler = BackgroundScheduler()
trigger = CronTrigger(hour=23,minute=0,second=0)

def daily_sync():
    with SessionLocal() as session:
        synchronize_daily_suggestion_data(session)

def start_scheduler():
    scheduler.add_job(daily_sync, trigger)
    scheduler.start()