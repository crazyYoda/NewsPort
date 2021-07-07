from django.urls import path, include
from .views import PostsList, PostDetailView, PostSearch, PostCreateView, PostUpdateView, PostDeleteView, Subscriber
from .views import upgrade_me


class ProductDeleteView:
    pass


urlpatterns = [
    path('', PostsList.as_view()),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('search/', PostSearch.as_view()),
    path('create/', PostCreateView.as_view(), name='posts_create'),
    path('create/<int:pk>', PostUpdateView.as_view(), name='post_update'),
    path('delete/<int:pk>', PostDeleteView.as_view(), name='post_delete'),
    path('upgrade/', upgrade_me, name='upgrade'),
    path('category/<int:pk>/subscribe/', Subscriber.as_view(), name='subscribe'),
]