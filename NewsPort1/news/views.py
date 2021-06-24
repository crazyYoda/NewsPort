from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from .models import Post
from datetime import datetime
from .filter import PostsFilter
from .forms import PostForm


class PostsList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')
    paginate_by = 10

    # form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        # context['form'] = PostForm()
        return context

    # def post(self, request, *args, **kwargs):
    #     form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса
    #
    #     if form.is_valid():
    #         form.save()

    #    return super().get(request, *args, **kwargs)


# дженерик для получения деталей о посте
class PostDetailView(DetailView):
    template_name = 'post_detail.html'
    queryset = Post.objects.all()

# дженерик для создания объекта
class PostCreateView(CreateView):
    template_name = 'posts_create.html'
    form_class = PostForm


# class PostsDetailView(DetailView):
#     model = Post
#     template_name = 'post.html'
#     context_object_name = 'post'


class PostSearch(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'search'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostsFilter(self.request.GET, queryset=self.get_queryset())  # вписываю фильтр в контекст
        return context


# дженерик для редактирования объекта
class PostUpdateView(UpdateView):
    template_name = 'posts_create.html'
    form_class = PostForm

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления поста
class PostDeleteView(DeleteView):
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/posts/'