from django.core.mail import mail_admins
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, TemplateView
from .models import Post, Author, Category, PostCategory, Comment
from datetime import datetime
from .filter import PostsFilter
from .forms import PostForm

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver # импортируем нужный декоратор


class PostsList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')
    paginate_by = 10
    form_class = PostForm

    def get_filter(self):
        return PostsFilter(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['categories'] = Category.objects.all()
        return context


class PostDetailView(PermissionRequiredMixin, DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'
    permission_required = ('news.add_post',)

    def get_context_data(self, *args, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        try:
            context['PCC'] = PostCategory.objects.get(postThrough=self.kwargs['pk']).categoryThrough
            context['all_category'] = Category.objects.get(post=self.kwargs.get('pk'))
            context['is_subscriber'] = Category.objects.get(post=self.kwargs.get('pk')).subscribers.filter(username=self.request.user).exists()

        except Comment.DoesNotExist:
            context['PCC'] = None
            context['all_category'] = None
        return context

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.get_object().id})


# дженерик для создания объекта
class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'posts_create.html'
    form_class = PostForm
    permission_required = ('news.add_post',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_premium'] = not self.request.user.groups.filter(name='authors').exists()
        return context

    # def post(self, request, *args, **kwargs):
    #
    #     send_mail(
    #         subject=f'{PostCategory.categoryThrough}',
    #         message=f'{user, Post.text}',
    #         from_email='aiki_neru@mail.ru',
    #
    #     )


class PostSearch(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'search'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostsFilter(self.request.GET, queryset=self.get_queryset())  # вписываю фильтр в контекст
        return context


# дженерик для редактирования объекта
class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'posts_create.html'
    form_class = PostForm
    permission_required = ('news.change_post',)

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся
    # редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления поста
class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/posts/'
    permission_required = ('news.delete_post',)



@login_required
def upgrade_me(request):
    user = request.user
    premium_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        premium_group.user_set.add(user)

    if not Author.objects.filter(authorUser=user).exists():
        Author.objects.create(authorUser=user)

    return redirect('/create/')


class Subscriber(UpdateView):
    model = Category

    def post(self, request, *args, **kwargs):

        if not Category.objects.get(pk=self.kwargs.get('pk')).subscribers.filter(username=self.request.user).exists():
            Category.objects.get(pk=self.kwargs.get('pk')).subscribers.add(self.request.user)
        else:
            Category.objects.get(pk=self.kwargs.get('pk')).subscribers.remove(self.request.user)
        return redirect(request.META.get('HTTP_REFERER'))


# @receiver(m2m_changed, sender=Post.postCategory.through)
# def notify_subscribers_categories(sender, instance, **kwargs):
#     new_post_categories = Post.objects.order_by('-id')[0].postCategory.all()
#     print(new_post_categories)
#     subject = f'Новая статья в категории: {instance.postCategory.values("name")}'
#     mail_admins(
#         subject=subject,
#         message= f'{instance.title}'
#     )


