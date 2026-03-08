import logging
from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

logger = logging.getLogger(__name__)


def crawl_job():
    from crawler import run
    logger.info("Crawler job started")
    run()
    logger.info("Crawler job finished")


class Command(BaseCommand):
    help = "Start APScheduler to run the crawler every 30 minutes"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone="Asia/Taipei")
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            crawl_job,
            trigger=CronTrigger(minute="*/30"),
            id="crawl_nba_news",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Scheduler started. Crawler will run every 30 minutes.")

        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
            logger.info("Scheduler stopped.")
