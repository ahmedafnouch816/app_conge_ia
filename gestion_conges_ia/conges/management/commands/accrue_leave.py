import calendar
import datetime
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from conges.models import Employe, LeaveAccrualRecord
from conges.utils.leave_accrual import process_accruals_for_month


class Command(BaseCommand):
    help = 'Process leave accruals for all employees for a specific month or the previous month'

    def add_arguments(self, parser):
        # Optional arguments to specify month and year
        parser.add_argument(
            '--month', 
            type=int, 
            help='Month to process (1-12). Defaults to previous month.'
        )
        parser.add_argument(
            '--year', 
            type=int, 
            help='Year to process. Defaults to current year or previous year if processing previous December.'
        )
        parser.add_argument(
            '--finalize', 
            action='store_true', 
            help='Finalize accruals and add to employee leave balances'
        )
        parser.add_argument(
            '--employee-id', 
            type=int, 
            help='Process only for a specific employee ID'
        )

    def handle(self, *args, **options):
        # Get month and year from options or default to previous month
        today = timezone.now().date()
        previous_month = today - relativedelta(months=1)
        
        month = options.get('month') or previous_month.month
        year = options.get('year') or previous_month.year
        
        # Validate month
        if month < 1 or month > 12:
            raise CommandError(f"Invalid month: {month}. Month must be between 1 and 12.")
        
        # Get finalize flag
        finalize = options.get('finalize', False)
        
        # Process for specific employee or all employees
        employee_id = options.get('employee_id')
        
        if employee_id:
            try:
                employee = Employe.objects.get(pk=employee_id)
                self.stdout.write(f"Processing leave accrual for employee: {employee}")
                
                from conges.utils.leave_accrual import update_or_create_accrual_record
                record = update_or_create_accrual_record(
                    employe=employee,
                    year=year,
                    month=month,
                    is_finalized=finalize
                )
                
                self.stdout.write(self.style.SUCCESS(
                    f"Processed accrual for {employee}: {record.leave_accrued} days for {calendar.month_name[month]} {year}"
                ))
                
            except Employe.DoesNotExist:
                raise CommandError(f"Employee with ID {employee_id} does not exist.")
        else:
            # Process for all employees
            self.stdout.write(f"Processing leave accruals for all employees for {calendar.month_name[month]} {year}")
            
            records = process_accruals_for_month(year, month, finalize)
            
            self.stdout.write(self.style.SUCCESS(
                f"Successfully processed {len(records)} leave accrual records for {calendar.month_name[month]} {year}"
            ))
            
            # Print summary
            total_accrued = sum(record.leave_accrued for record in records)
            self.stdout.write(f"Total leave accrued: {total_accrued:.2f} days")
            
            if finalize:
                self.stdout.write(self.style.SUCCESS("Accruals have been finalized and added to employee balances"))
            else:
                self.stdout.write(self.style.WARNING(
                    "Accruals have NOT been finalized. Run with --finalize to apply to employee balances."
                ))
