# PSL
import os

# Third part
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skills_finder_web.settings")

application = get_wsgi_application()
