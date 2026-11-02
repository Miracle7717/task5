from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from blog.models import Blog

from .forms import BlogForm


class BlogManageListView(ListView):
    model = Blog
    template_name = "blog_crud/blog_list.html"
    context_object_name = "blogs"
    ordering = ["pk"]


class BlogManageDetailView(DetailView):
    model = Blog
    template_name = "blog_crud/blog_detail.html"
    context_object_name = "blog"


class BlogCreateView(CreateView):
    model = Blog
    form_class = BlogForm
    template_name = "blog_crud/blog_form.html"
    success_url = reverse_lazy("blog_crud:blog_list")


class BlogUpdateView(UpdateView):
    model = Blog
    form_class = BlogForm
    template_name = "blog_crud/blog_form.html"
    success_url = reverse_lazy("blog_crud:blog_list")


class BlogDeleteView(DeleteView):
    model = Blog
    template_name = "blog_crud/blog_confirm_delete.html"
    success_url = reverse_lazy("blog_crud:blog_list")
