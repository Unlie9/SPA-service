import os
import django
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter

from jwt_middleware import JwtAuthMiddlewareStack


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comments_service.settings')
django.setup()

from comments import routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
