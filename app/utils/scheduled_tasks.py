from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

    
scheduler = BackgroundScheduler()
trigger = CronTrigger(hour=23,minute=0,second=0)


def daily_sync():
    print('daily_task')

def start_scheduler():
    scheduler.add_job(daily_sync, trigger)
    scheduler.start()