from django.urls import path

from .views import all_questions, answer, crystal_ball, index

app_name = 'crystal_ball'


urlpatterns = [
    path('', index, name='index'),
    path('<slug:deck_slug>/', crystal_ball, name='question'),
    path('answer/<int:id>/', answer, name='answer'),
    path('all_questions/<int:id>/', all_questions, name='all_questions'),
]
