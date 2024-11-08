import os
from django.core.wsgi import get_wsgi_application

# Ensure the correct settings module is set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atip_tracker.settings')

application = get_wsgi_application()
