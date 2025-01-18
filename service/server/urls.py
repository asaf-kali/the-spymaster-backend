from django.urls import include, path
from rest_framework import routers

from .views import IndexView, auth
from .views.game.base import GameView
from .views.game.classic import ClassicGameView
from .views.game.duet import DuetGameView
from .views.game.mini import MiniGameView

router_v1 = routers.SimpleRouter()
router_v1.register(r"users", viewset=auth.UserDetailsView, basename="users")
router_v1.register(r"game", viewset=GameView, basename="game")
router_v1.register(r"game/classic", viewset=ClassicGameView, basename="classic")
router_v1.register(r"game/duet", viewset=DuetGameView, basename="duet")
router_v1.register(r"game/mini", viewset=MiniGameView, basename="mini")

urlpatterns = [
    path("", view=IndexView.as_view(), name="index"),
    path("api/v1/", view=include(router_v1.urls)),
    path("auth/google/oauth/", view=auth.oauth2_login, name="google_oauth"),
    path("auth/google/callback/", view=auth.oauth2_callback, name="google_callback"),
    path("auth/login-complete/", view=auth.LoginCallbackView.as_view(), name="login_complete"),
    path("auth/logout/", view=auth.LogoutView.as_view(), name="logout"),
]
