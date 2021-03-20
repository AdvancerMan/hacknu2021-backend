from django.urls import path

from .views import (
    AuthView, StartFindBattleView, StopFindBattleView, MatchBattleView,
    StartBattleView, BattleResultsView,
    AuthView, StartFindBattleView,
    StopFindBattleView, MatchBattleView, EverydayRewardView
)

urlpatterns = [
    path('auth', AuthView.as_view()),
    path('battle/find/start', StartFindBattleView.as_view()),
    path('battle/find/stop', StopFindBattleView.as_view()),
    path('battle/find/match', MatchBattleView.as_view()),
    path('everyday/reward', EverydayRewardView.as_view()),
    path('battle/ready', StartBattleView.as_view()),
    path('battle/results', BattleResultsView.as_view()),
]
