from django.urls import include, path


urlpatterns = [
    path("", include("blog.urls")),
    path("manage/", include("blog_crud.urls")),
]
