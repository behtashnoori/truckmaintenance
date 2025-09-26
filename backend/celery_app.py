"""
Celery configuration for background tasks
"""
import os
from celery import Celery
from kombu import Queue

# Redis URL for Celery broker and result backend
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery instance
celery_app = Celery(
    'truckmaintenance',
    broker=redis_url,
    backend=redis_url,
    include=['backend.tasks']
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        'backend.tasks.process_bulk_upload': {'queue': 'bulk_upload'},
        'backend.tasks.send_notification': {'queue': 'notifications'},
        'backend.tasks.cleanup_temp_files': {'queue': 'maintenance'},
    },
    
    # Queue configuration
    task_default_queue='default',
    task_queues=(
        Queue('default', routing_key='default'),
        Queue('bulk_upload', routing_key='bulk_upload'),
        Queue('notifications', routing_key='notifications'),
        Queue('maintenance', routing_key='maintenance'),
    ),
    
    # Task execution
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Tehran',
    enable_utc=True,
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes
    
    # Result backend
    result_expires=3600,  # 1 hour
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'cleanup-temp-files': {
            'task': 'backend.tasks.cleanup_temp_files',
            'schedule': 3600.0,  # Every hour
        },
        'send-daily-reports': {
            'task': 'backend.tasks.send_daily_reports',
            'schedule': 86400.0,  # Daily
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['backend.tasks'])
