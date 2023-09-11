import calendar
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config

weekday_choices = ((1, _('Montag')),
                   (2, _('Dienstag')),
                   (3, _('Mittwoch')),
                   (4, _('Donnerstag')),
                   (5, _('Freitag')),
                   (6, _('Samstag')),
                   (7, _('Sonntag')))

weekdays = dict(weekday_choices)


def is_date_in_cancelation_period(date):
    return start_of_business_year() <= date <= cancelation_date()


def days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


def start_of_business_year():
    day = Config.business_year_start()['day']
    month = Config.business_year_start()['month']
    return calculate_last(day, month)


def end_of_business_year():
    return start_of_next_business_year() - timedelta(days=1)


def start_of_next_business_year():
    day = Config.business_year_start()['day']
    month = Config.business_year_start()['month']
    return calculate_next(day, month)


def end_of_next_business_year():
    tmp = start_of_next_business_year()
    return datetime.date(tmp.year + 1, tmp.month, tmp.day) - timedelta(days=1)


def start_of_specific_business_year(refdate):
    day = Config.business_year_start()['day']
    month = Config.business_year_start()['month']
    return calculate_last_offset(day, month, refdate)


def end_of_specific_business_year(refdate):
    day = Config.business_year_start()['day']
    month = Config.business_year_start()['month']
    return calculate_next_offset(day, month, refdate) - timedelta(days=1)


def next_cancelation_date():
    """
    :return: next cancelation deadline from today
    """
    return next_cancelation_date_from(datetime.date.today())


def cancelation_date():
    """
    :return: cancelation deadline for current business year
    """
    return next_cancelation_date_from(start_of_business_year())


def next_cancelation_date_from(start):
    c_month = Config.business_year_cancelation_month()
    if start.month <= c_month:
        year = start.year
    else:
        year = start.year + 1
    return datetime.date(year, c_month, days_in_month(year, c_month))


def next_membership_end_date():
    """
    :return: end date of membership when canceling now
    """
    endmonth = Config.membership_end_month()
    noticemonths = Config.membership_end_notice_period()
    nowplusnotice = datetime.date.today() + relativedelta(months=noticemonths)
    if nowplusnotice.month <= endmonth:
        endyear = nowplusnotice.year
    else:
        endyear = nowplusnotice.year + 1
    day = days_in_month(endyear, endmonth)
    return datetime.date(endyear, endmonth, day)


def calculate_next(day, month):
    return calculate_next_offset(day, month, datetime.date.today())


def calculate_last(day, month):
    return calculate_last_offset(day, month, datetime.date.today())


def calculate_next_offset(day, month, offset):
    if offset.month < month or (offset.month == month and offset.day < day):
        year = offset.year
    else:
        year = offset.year + 1
    return datetime.date(year, month, day)


def calculate_last_offset(day, month, offset):
    if offset.month > month or (offset.month == month and offset.day >= day):
        year = offset.year
    else:
        year = offset.year - 1
    return datetime.date(year, month, day)


def calculate_remaining_days_percentage(date):
    return (end_of_business_year() - date).days / (end_of_business_year() - start_of_business_year()).days


month_choices = ((1, _('Januar')),
                 (2, _('Februar')),
                 (3, _('März')),
                 (4, _('April')),
                 (5, _('Mai')),
                 (6, _('Juni')),
                 (7, _('Juli')),
                 (8, _('August')),
                 (9, _('September')),
                 (10, _('Oktober')),
                 (11, _('November')),
                 (12, _('Dezember')))


def default_to_business_year(func):
    """
    decorator: defaults the first 2 arguments to start and end of current business year.
    """
    def wrapper(start=None, end=None, *args, **kwargs):
        return func(start or start_of_business_year(), end or end_of_business_year(), *args, **kwargs)
    return wrapper
