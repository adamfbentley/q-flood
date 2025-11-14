from celery import Celery
from app.core.config import settings

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
    # Autodiscover tasks in the 'app.tasks' package
    include=['app.tasks.geospatial_tasks', 'app.tasks.matrix_tasks', 'app.tasks.solver_tasks', 'app.tasks.quantum_tasks', 'app.tasks.postprocessing_tasks'] # Added geospatial_tasks
)
