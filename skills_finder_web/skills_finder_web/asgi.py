# PSL
import os

# Third part
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skills_finder_web.settings")

application = get_asgi_application()
