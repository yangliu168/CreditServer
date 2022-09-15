from django.urls import path
from .views import ScoreView,ScoresView,MissionView,test

urlpatterns =[
    # v1/score/user
    path('user', ScoreView.as_view()),
    # v1/score/users
    path('users', ScoresView.as_view()),
    # v1/score/mission
    path('mission', MissionView.as_view()),
    # v1/score/test
    path('test', test),
]