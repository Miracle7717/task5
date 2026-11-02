from django.test import TestCase
from django.urls import reverse

from .models import Blog


class BlogListTests(TestCase):
    def test_empty_list_shows_empty_message(self):
        response = self.client.get(reverse("blog:blog_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Статей пока нет.")

    def test_list_shows_all_blog_titles(self):
        first = Blog.objects.create(title="Первая статья", content="Текст 1")
        second = Blog.objects.create(title="Вторая статья", content="Текст 2")

        response = self.client.get(reverse("blog:blog_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, first.title)
        self.assertContains(response, second.title)
        self.assertEqual(list(response.context["blogs"]), [first, second])

    def test_list_links_to_each_detail_page_by_id(self):
        blog = Blog.objects.create(title="Переход", content="Текст")

        response = self.client.get(reverse("blog:blog_list"))
        detail_url = reverse("blog:blog_detail", args=[blog.pk])

        self.assertContains(
            response,
            f'href="{detail_url}"',
        )
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, blog.content)

    def test_list_with_no_matching_content_does_not_show_unrelated_title(self):
        Blog.objects.create(title="Другая статья", content="Текст")

        response = self.client.get(reverse("blog:blog_list"))

        self.assertNotContains(response, "Несуществующая статья")


class BlogDetailTests(TestCase):
    def test_new_blog_starts_with_zero_likes(self):
        blog = Blog.objects.create(title="Новая статья", content="Текст")

        self.assertEqual(blog.likes, 0)

    def test_detail_shows_content_and_increments_likes(self):
        blog = Blog.objects.create(title="Подробности", content="Содержимое статьи")

        response = self.client.get(reverse("blog:blog_detail", args=[blog.pk]))

        blog.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, blog.title)
        self.assertContains(response, blog.content)
        self.assertEqual(blog.likes, 1)

    def test_each_detail_visit_increments_likes(self):
        blog = Blog.objects.create(title="Популярная", content="Текст")
        url = reverse("blog:blog_detail", args=[blog.pk])

        self.client.get(url)
        self.client.get(url)

        blog.refresh_from_db()
        self.assertEqual(blog.likes, 2)

    def test_detail_for_unknown_id_returns_404(self):
        response = self.client.get(reverse("blog:blog_detail", args=[999]))

        self.assertEqual(response.status_code, 404)

    def test_detail_has_link_back_to_list(self):
        blog = Blog.objects.create(title="Назад", content="Текст")

        response = self.client.get(reverse("blog:blog_detail", args=[blog.pk]))

        self.assertContains(
            response,
            f'href="{reverse("blog:blog_list")}"',
        )
