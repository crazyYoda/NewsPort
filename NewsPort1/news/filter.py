from django_filters import FilterSet
from .models import Post


# создаю фильтр
class PostsFilter(FilterSet):
    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            'time_post': ['gte'],
            'author__authorUser': ['exact'],
        }
