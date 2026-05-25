"""
Configuration module for Hoop It Up Backend
Uses python-decouple to load environment variables
"""
from decouple import config


class Config:
    """Application configuration from environment variables"""
    
    # Secret key for Flask sessions and CSRF protection
    # Default to a development key, but should be set in production via env var
    SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-in-production')
    
    # Domain name for the application
    # Used for CORS and frontend connection URLs
    DOMAIN_NAME = config('DOMAIN_NAME', default='localhost')
    
    # Flask environment
    FLASK_ENV = config('FLASK_ENV', default='production')
    
    # Debug mode (should be False in production)
    DEBUG = config('DEBUG', default=False, cast=bool)
    
    # CORS allowed origins
    CORS_ALLOWED_ORIGINS = config(
        'CORS_ALLOWED_ORIGINS',
        default='*'
    )
    
    # Scheduled message configuration
    # Cron expression for when to send the message (default: 7 AM on Tue/Thu)
    SCHEDULE_CRON = config(
        'SCHEDULE_CRON',
        default='0 7 * * 2,4'
    )
    
    # Message to send on the schedule
    SCHEDULE_MESSAGE = config(
        'SCHEDULE_MESSAGE',
        default='Game today @ 4:30?'
    )
    
    # Timezone for cron schedule
    SCHEDULE_TIMEZONE = config(
        'SCHEDULE_TIMEZONE',
        default='UTC'
    )

    # Daily summary time (HH:MM) to send a daily summary message
    # Example: '12:00' sends summary every day at 12:00 (server timezone configured by SCHEDULE_TIMEZONE)
    SCHEDULE_SUMMARY_TIME = config('SCHEDULE_SUMMARY_TIME', default='12:00')
