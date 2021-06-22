from django.urls import path
from .views import PostsList, PostsDetail, PostSearch

urlpatterns = [
    path('', PostsList.as_view()),
    path('<int:pk>', PostsDetail.as_view()),
    path('search/', PostSearch.as_view()),
]