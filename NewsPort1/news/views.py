from django.views.generic import ListView, DetailView
from .models import Post
from datetime import datetime


class PostsList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        return context



class PostsDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'