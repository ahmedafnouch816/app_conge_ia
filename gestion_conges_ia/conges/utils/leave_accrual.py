import calendar
import datetime
from django.utils import timezone
from django.db import models
from django.db.models import Sum
from django.db import transaction

from conges.models import Employe, LeaveAccrualRecord


def get_workable_days(year, month):
    """
    Calculate the number of workable days in a month (excluding Sundays).
    
    Args:
        year: The year
        month: The month (1-12)
        
    Returns:
        int: Number of workable days
    """
    # Get number of days in the month
    _, num_days = calendar.monthrange(year, month)
    
    # Count non-Sunday days
    workable_days = 0
    for day in range(1, num_days + 1):
        # 6 is Sunday in calendar.weekday (0 is Monday)
        if calendar.weekday(year, month, day) != 6:
            workable_days += 1
    
    return workable_days


def get_days_worked(employe, year, month):
    """
    Get the number of days actually worked by an employee in a month.
    
    This is a placeholder implementation. In a real-world scenario, 
    this would connect to an attendance tracking system.
    
    Args:
        employe: The Employee object
        year: The year
        month: The month (1-12)
        
    Returns:
        int: Number of days worked
    """
    # TODO: Integrate with attendance tracking system
    # For now, we'll assume the employee worked all workable days
    # In a real implementation, this would check attendance records
    
    workable_days = get_workable_days(year, month)
    
    # Placeholder logic - assume employee worked all workable days
    # This should be replaced with actual attendance data
    return workable_days


def calculate_leave_accrual(employe, year, month, days_worked=None):
    """
    Calculate leave accrual for an employee for a specific month.
    
    Formula: (1.83 ÷ workable days in the month) × days actually worked
    
    Args:
        employe: The Employee object
        year: The year
        month: The month (1-12)
        days_worked: Optional - number of days worked (will be calculated if not provided)
        
    Returns:
        tuple: (workable_days, days_worked, leave_accrued)
    """
    # Base accrual rate per month
    BASE_ACCRUAL_RATE = 1.83
    
    # Get workable days in the month
    workable_days = get_workable_days(year, month)
    
    # Get days worked if not provided
    if days_worked is None:
        days_worked = get_days_worked(employe, year, month)
    
    # Calculate accrual using the formula
    leave_accrued = (BASE_ACCRUAL_RATE / workable_days) * days_worked
    
    # Round to 2 decimal places for precision
    leave_accrued = round(leave_accrued, 2)
    
    return (workable_days, days_worked, leave_accrued)


def update_or_create_accrual_record(employe, year, month, days_worked=None, is_finalized=False):
    """
    Update or create a leave accrual record for an employee for a specific month.
    
    Args:
        employe: The Employee object
        year: The year
        month: The month (1-12)
        days_worked: Optional - number of days worked (will be calculated if not provided)
        is_finalized: Whether to finalize the accrual and add to employee balance
        
    Returns:
        LeaveAccrualRecord: The created or updated record
    """
    # Calculate the accrual
    workable_days, days_worked, leave_accrued = calculate_leave_accrual(
        employe, year, month, days_worked
    )
    
    # Update or create the record
    record, created = LeaveAccrualRecord.objects.update_or_create(
        employe=employe,
        month=month,
        year=year,
        defaults={
            'workable_days': workable_days,
            'days_worked': days_worked,
            'leave_accrued': leave_accrued,
            'is_finalized': is_finalized
        }
    )
    
    # If finalizing, update employee's leave balance
    if is_finalized and not record.is_finalized:
        with transaction.atomic():
            employe.solde_de_conge += leave_accrued
            employe.save()
            
            # Mark as finalized
            record.is_finalized = True
            record.save()
    
    return record


def process_accruals_for_month(year, month, finalize=False):
    """
    Process leave accruals for all employees for a specific month.
    
    Args:
        year: The year
        month: The month (1-12)
        finalize: Whether to finalize accruals and add to employee balances
        
    Returns:
        list: List of created or updated LeaveAccrualRecord objects
    """
    records = []
    
    # Get all employees
    employees = Employe.objects.all()
    
    # Process each employee
    for employe in employees:
        record = update_or_create_accrual_record(
            employe=employe,
            year=year,
            month=month,
            is_finalized=finalize
        )
        records.append(record)
    
    return records
