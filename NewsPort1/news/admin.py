from django.contrib import admin
from .models import *


class PostAdmin (admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'time_post')
    list_display_links = ('title',)
    search_fields = ('title', 'text', 'category')
    list_filter = ('time_post', 'title')

class CategoryAdmin (admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    search_fields = ('name',)

admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(PostCategory)
admin.site.unregister(PostCategory)
admin.site.register(Comment)
