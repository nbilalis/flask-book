from flask import current_app as app

import locale
import timeago
from datetime import datetime
from dateutil import tz
from babel.dates import format_datetime


@app.template_filter('timeago')
def timeago_filter(value):
    '''
    Filter to show relative time deltas
    Date and Time — Babel 2.7.0 documentation - https://bit.ly/3iKciLj
    '''
    # return format_timedelta(value - datetime.utcnow(), add_direction=True)
    return timeago.format(value, now=datetime.utcnow())


@app.template_filter('currency')
def currency_filter(value):
    # locale.setlocale(locale.LC_ALL, 'el_GR')
    return locale.currency(value, symbol=True, grouping=True)


@app.template_filter('timestamp')
def timetamp_filter(value):
    # locale.setlocale(locale.LC_ALL, 'el_GR')
    # return value.strftime("%a, %d %b %Y %H:%M:%S")

    # python - Convert UTC datetime string to local datetime - Stack Overflow - https://bit.ly/3BGUHwn
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    utc = value.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)

    return format_datetime(local)
