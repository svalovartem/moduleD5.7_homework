from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from .models import Post
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator
from .filters import NewsFilter
from .forms import NewsForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import Group


class NewsList(ListView):
    model = Post
    template_name = 'posts/news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-id')
    ordering = ['-postDate']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return NewsFilter(self.request.GET, queryset=queryset).qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())
        context['choices'] = Post.CHOICES
        context['form'] = NewsForm
        context['author'] = not self.request.user.groups.filter(name='authors').exists()

        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)

@login_required
def become_author(request):
    user = request.user
    author = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author.user_set.add(user)
    return redirect('/news')


class NewsDetail(DetailView):
    model = Post
    template_name = 'posts/post.html'
    context_object_name = 'news_details'


class CreateNews(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ('news.add_post',)

    template_name = 'posts/adds/add.html'
    form_class = NewsForm


class UpdateNews(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)

    template_name = 'posts/adds/add.html'
    form_class = NewsForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class DeleteNews(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)

    model = Post
    context_object_name = "delete_news"
    template_name = 'posts/adds/delete_post.html'
    queryset = Post.objects.all()
    form_class = NewsForm
    success_url = reverse_lazy('news:posts')

class SearchList(ListView):
    model = Post
    template_name = 'posts/adds/search.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')
    ordering = ['-postDate']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())

        return context


# class Posts(View):
#
#     def get(self, request):
#         posts = Post.objects.order_by('-postDate')
#         pag = Paginator(posts, 10)
#         posts = pag.get_page(request.GET.get('page', 1))
#
#         context = {
#             'posts': posts
#         }
#
#         return render(request, 'posts/news.html', context)