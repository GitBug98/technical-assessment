"""
ASGI config for project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
asgi_app=get_asgi_application()


import project.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from users.middlewares import TokenAuthMiddleware


application = ProtocolTypeRouter({
    "http": asgi_app,
    # Just HTTP for now. (We can add other protocols later.)
    "websocket": TokenAuthMiddleware(
        URLRouter(
            # URLRouter just takes standard Django path() or url() entries.
            project.routing.websocket_urlpatterns
        ),
    ),

})
