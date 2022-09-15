from django.urls import path
from .views import ScoreView,MissionView

urlpatterns =[
    # v1/score/user
    path('user', ScoreView.as_view()),

    # v1/score/mission
    path('mission', MissionView.as_view()),
]