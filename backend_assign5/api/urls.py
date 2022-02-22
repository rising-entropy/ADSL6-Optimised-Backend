from .views import *
from django.urls import path, include

urlpatterns = [
    path('/login', LoginAPI.as_view(), name='LoginAPI'),
    path('/quizzes', QuizzesAPI.as_view(), name='QuizzesAPI'),
    path('/quiz/<int:id>', QuizAPI.as_view(), name='QuizAPI'),
    path('/questions', QuestionsAPI.as_view(), name='QuestionsAPI'),
    path('/questions/<int:id>', Questions2API.as_view(), name='Questions2API'),
    path('/question/<int:id>', QuestionAPI.as_view(), name='QuestionAPI'),
    path('/score/<int:id>', ScoresAPI.as_view(), name='ScoresAPI')
]