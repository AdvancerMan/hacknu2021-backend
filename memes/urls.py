from django.urls import path

from .views import (
    StartBattleView, BattleResultsView, AuthView, StartFindBattleView,
    StopFindBattleView, MatchBattleView, EverydayRewardView,
    MyCreatorsLeaderboardView, CreatorsLeaderboardView, MyBattleLeaderboardView,
    BattleLeaderboardView, AddLikeCardView, RemoveLikeCardView
)

urlpatterns = [
    path('auth', AuthView.as_view()),
    path('battle/find/start', StartFindBattleView.as_view()),
    path('battle/find/stop', StopFindBattleView.as_view()),
    path('battle/find/match', MatchBattleView.as_view()),
    path('battle/ready', StartBattleView.as_view()),
    path('battle/results', BattleResultsView.as_view()),
    path('battle/leaderboard', BattleLeaderboardView.as_view()),
    path('battle/leaderboard/my', MyBattleLeaderboardView.as_view()),

    path('cards/like/add', AddLikeCardView.as_view()),
    path('cards/like/remove', RemoveLikeCardView.as_view()),
    path('cards/creators/leaderboard', CreatorsLeaderboardView.as_view()),
    path('cards/creators/leaderboard/my', MyCreatorsLeaderboardView.as_view()),

    path('everyday/reward', EverydayRewardView.as_view()),
]
