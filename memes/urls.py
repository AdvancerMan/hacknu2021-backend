from django.urls import path

from .views import (
    AuthView, StartFindBattleView,
    StopFindBattleView, MatchBattleView, EverydayRewardView
)

urlpatterns = [
    path('auth', AuthView.as_view()),
    path('battle/find/start', StartFindBattleView.as_view()),
    path('battle/find/stop', StopFindBattleView.as_view()),
    path('battle/find/match', MatchBattleView.as_view()),
    path('reward', EverydayRewardView.as_view())
]
