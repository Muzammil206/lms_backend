import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appstore.settings')

# Configure Django
django.setup()

from .models import *
from .utils import *
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class WatchPlan():
    base = ""
    
    def check_all(self):
        self.check_matured_plans()
        self.check_next_savings()
    
    def check_matured_plans(self):
        plans = Plan.objects.filter(matured=False, active=True)
        for p in plans:
            if self.is_today(p.end_date) or self.is_past(p.end_date):
                p.matured = True
                p.save()
                emails = [s.email for s in p.members.all()]
                amt = 0
                for a in p.savings.all():
                    amt += a.amount
                send_maturity_notification(emails, p.title, p.end_date, amt)
            else:
                pass
        try:
            today_task = Task.objects.get(date=date.today())
            today_task.check_matured = True
            today_task.save()
        except:
            today_task = Task(date=date.today(), check_matured=True)
            today_task.save()
        
    
    def check_next_savings(self):
        plans = Plan.objects.filter(matured=False, active=True)
        for p in plans:
            emails = [s.email for s in p.members.all()]
            if self.is_today(p.next_savings) or self.is_past(p.next_savings):
                if self.is_today(p.next_savings):
                    send_saving_reminder(emails, p.title, "today")
                if p.frequency == "daily":
                    p.next_savings = self.add_one_day()
                    p.save()
                elif p.frequency == "weekly":
                    p.next_savings = self.add_one_week()
                    p.save()
                elif p.frequency == "monthly":
                    p.next_savings = self.add_one_month()
                    p.save()
            elif self.is_tomorrow(p.next_savings):
                send_saving_reminder(emails, p.title, "tomorrow")
        try:
            today_task = Task.objects.get(date=date.today())
            today_task.check_savings = True
            today_task.save()
        except:
            today_task = Task(date=date.today(), check_savings=True)
            today_task.save()
    
    def is_today(self, n_date):
        return n_date == date.today()
    
    def is_tomorrow(self, n_date):
        return n_date == date.today() + timedelta(days=1)
    
    def is_past(self, n_date):
        return n_date < date.today()
    
    def add_one_day(self):
        date_field = date.today() + timedelta(days=1)
        return date_field

    def add_one_week(self):
        date_field = date.today() + timedelta(weeks=1)
        return date_field

    def add_one_month(self):
        date_field = date.today() + relativedelta(months=1)
        return date_field

if __name__ == "__main__":
    my_plan = WatchPlan()
    my_plan.check_all()