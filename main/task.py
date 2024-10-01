import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ajo_backend.settings')

# Configure Django
django.setup()

from .models import *
from .utils import *
from django.utils import timezone
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import string
import random

def generate(n):
    chars = string.ascii_lowercase + string.digits
    random_combination = ''.join(random.choice(chars) for _ in range(n))
    return random_combination

class WatchPlan():
    base = ""
    
    def check_all(self):
        self.remove_unpaid_transactions()
        self.check_target_interest()
        self.check_matured_target_plans()
        self.check_next_target_savings()
    
    def remove_unpaid_transactions(self):
        trans = WalletTransaction.objects.filter(transactionStatus="unpaid")
        trans2 = Saving.objects.filter(status="pending")
        for t in trans:
            if self.is_past(t.date.date()):
                t.delete()
        for tr in trans2:
            if self.is_past(tr.date.date()):
                tr.delete()
        try:
            today_task = Task.objects.get(date=date.today())
            today_task.remove_unpaid_transactions = True
            today_task.save()
        except:
            today_task = Task(date=date.today(), remove_unpaid_transactions=True)
            today_task.save()
    
    def check_matured_target_plans(self):
        plans = SavingPlan.objects.filter(matured=False, active=True)
        for p in plans:
            if self.is_today(p.end_date) or self.is_past(p.end_date):
                p.matured = True
                p.save()
                send_maturity_notification(p.user, p)
            else:
                pass
        try:
            today_task = Task.objects.get(date=date.today())
            today_task.check_matured_target = True
            today_task.save()
        except:
            today_task = Task(date=date.today(), check_matured_target=True)
            today_task.save()
        
    def check_next_target_savings(self):
        plans = SavingPlan.objects.filter(matured=False, active=True)
        for p in plans:
            if self.is_today(p.next_savings) or self.is_past(p.next_savings):
                if self.is_today(p.next_savings):
                    if not p.auto_save:
                        send_saving_reminder(p.user, p.title, "today")
                    else:
                        account = Account.objects.get(user=p.user)
                        if account.walletBalance < decimal.Decimal(p.saving_amount):
                            send_saving_error(p.user, p)
                        else:
                            new_contrib = Saving(
                                plan_ref=p.reference, type="Topup", amount=decimal.Decimal(p.saving_amount),
                                payment_method="Wallet Balance", reference=f"{generate(20)}"
                                )
                            new_contrib.save()
                            account.sub_funds(new_contrib.amount)
                            p.add_funds(new_contrib.amount)
                            new_contrib.status = "success"
                            new_contrib.new_balance = p.balance
                            new_contrib.save()
                            Notification.objects.create(
                                user=p.user, title=f"{p.title} Topup", details={
                                    "type": "saving",
                                    "message": f"Your NGN{new_contrib.amount} automatic topup is successful."
                                }
                            )
                            send_autosaving_notification(p.user, p, new_contrib.amount)
                if p.frequency == "daily":
                    p.next_savings = self.add_one_day()
                    if p.next_savings > p.end_date:
                        p.next_savings = p.end_date
                    p.save()
                elif p.frequency == "weekly":
                    p.next_savings = self.add_one_week()
                    if p.next_savings > p.end_date:
                        p.next_savings = p.end_date
                    p.save()
                elif p.frequency == "monthly":
                    p.next_savings = self.add_one_month()
                    if p.next_savings > p.end_date:
                        p.next_savings = p.end_date
                    p.save()
            elif self.is_tomorrow(p.next_savings):
                send_saving_reminder(p.user, p.title, "tomorrow")
        try:
            today_task = Task.objects.get(date=date.today())
            today_task.check_next_target_saving = True
            today_task.save()
        except:
            today_task = Task(date=date.today(), check_next_target_saving=True)
            today_task.save()
    
    def check_target_interest(self):
        plans = SavingPlan.objects.filter(matured=False, active=True, interest_enabled=True)
        for p in plans:
            amount_dec = decimal.Decimal(p.interest_rate / 100) * (p.balance / 12)
            amount = amount_dec.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
            if not p.interest:
                if self.is_past_month(p.start_date):
                    p.add_interest(amount)
                    Saving.objects.create(
                        plan_ref=p.reference, type="Interest", status="success", amount=decimal.Decimal(amount),
                        reference=f"{generate(20)}", new_balance=p.balance
                    )
                    Notification.objects.create(
                    user=p.user, title=f"{p.title} Savings Interest", details={
                        "type": "saving",
                        "message": f"NGN{amount} interest has been paid into your savings."
                    }
                )
            else:
                int_dates = p.interest["date"]
                last_interest = int_dates[len(int_dates) - 1]
                last_date = datetime.strptime(last_interest, "%Y-%m-%d").date()
                if self.is_past_month(last_date):
                    p.add_interest(amount)
                    Saving.objects.create(
                        plan_ref=p.reference, type="Interest", status="success", amount=decimal.Decimal(amount),
                        reference=f"{generate(20)}", new_balance=p.balance
                    )
                    Notification.objects.create(
                    user=p.user, title=f"{p.title} Savings Interest", details={
                        "type": "saving",
                        "message": f"NGN{amount} interest has been paid into your savings."
                    })
        try:
            today_task = Task.objects.get(date=date.today())
            today_task.check_target_interest = True
            today_task.save()
        except:
            today_task = Task(date=date.today(), check_target_interest=True)
            today_task.save()
     
    
    def is_today(self, n_date):
        return n_date == date.today()
    
    def is_tomorrow(self, n_date):
        return n_date == date.today() + timedelta(days=1)
    
    def is_past(self, n_date):
        return n_date < date.today()

    def is_past_month(self, n_date):
        return n_date == date.today() - timedelta(days=30)
    
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