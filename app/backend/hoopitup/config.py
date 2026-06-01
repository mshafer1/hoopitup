"""
Configuration module for Hoop It Up Backend
Uses python-decouple to load environment variables
"""

from decouple import config

SECRET_KEY = config(
    "SECRET_KEY",
)
"""
Secret key for Flask sessions and CSRF protection (required).
"""

DEBUG = config("DEBUG", default=False, cast=bool)
"""
Debug mode (should be False in production).
"""

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="none")
"""
CORS allowed origins.
"""

SCHEDULE_CRON = config("SCHEDULE_CRON", default="0 7 * * 2,4")
"""
Scheduled message configuration.
Cron expression for when to send the message (default: 7 AM on Tue/Thu).
"""

SCHEDULE_MESSAGE = config("SCHEDULE_MESSAGE", default="Game today @ 4:30?")
"""
Message to send on the schedule.
"""

SCHEDULE_TIMEZONE = config("SCHEDULE_TIMEZONE", default="UTC")
"""
Timezone for cron schedule.
"""

SCHEDULE_SUMMARY_TIME = config("SCHEDULE_SUMMARY_TIME", default=None)
"""
Daily summary time (HH:MM) to send a daily summary message.
Example: '12:00' sends summary every day at 12:00 (server timezone configured by SCHEDULE_TIMEZONE).
"""
