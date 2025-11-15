from celery import Celery
from backend.core.config import settings

celery_app = Celery(
    "flood_forecasting",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    # Autodiscover tasks in the 'backend.tasks' package
    include=['backend.tasks.geospatial_tasks', 'backend.tasks.matrix_tasks', 'backend.tasks.solver_tasks', 'backend.tasks.quantum_tasks', 'backend.tasks.postprocessing_tasks']
)
