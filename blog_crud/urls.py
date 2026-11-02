from django.urls import path

from . import views


app_name = "blog_crud"

urlpatterns = [
    path("blogs/", views.BlogManageListView.as_view(), name="blog_list"),
    path("blogs/create/", views.BlogCreateView.as_view(), name="blog_create"),
    path("blogs/<int:pk>/", views.BlogManageDetailView.as_view(), name="blog_detail"),
    path("blogs/<int:pk>/edit/", views.BlogUpdateView.as_view(), name="blog_update"),
    path("blogs/<int:pk>/delete/", views.BlogDeleteView.as_view(), name="blog_delete"),
]
