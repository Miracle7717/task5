from django.test import TestCase
from django.urls import reverse

from blog.models import Blog


class BlogCrudTests(TestCase):
    def setUp(self):
        self.blog = Blog.objects.create(
            title="Исходная статья",
            content="Исходное содержимое",
        )

    def test_list_shows_blog_and_crud_links(self):
        response = self.client.get(reverse("blog_crud:blog_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.blog.title)
        self.assertContains(
            response,
            reverse("blog_crud:blog_update", args=[self.blog.pk]),
        )
        self.assertContains(
            response,
            reverse("blog_crud:blog_delete", args=[self.blog.pk]),
        )

    def test_detail_shows_blog_content(self):
        response = self.client.get(
            reverse("blog_crud:blog_detail", args=[self.blog.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.blog.title)
        self.assertContains(response, self.blog.content)

    def test_create_saves_blog_and_redirects(self):
        response = self.client.post(
            reverse("blog_crud:blog_create"),
            {"title": "Новая статья", "content": "Новый текст"},
        )

        self.assertRedirects(response, reverse("blog_crud:blog_list"))
        self.assertTrue(
            Blog.objects.filter(title="Новая статья", content="Новый текст").exists()
        )

    def test_create_rejects_blank_title(self):
        response = self.client.post(
            reverse("blog_crud:blog_create"),
            {"title": "", "content": "Текст"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Blog.objects.filter(content="Текст").exists())

    def test_update_changes_blog_and_redirects(self):
        response = self.client.post(
            reverse("blog_crud:blog_update", args=[self.blog.pk]),
            {"title": "Обновлённая статья", "content": "Обновлённый текст"},
        )

        self.assertRedirects(response, reverse("blog_crud:blog_list"))
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, "Обновлённая статья")
        self.assertEqual(self.blog.content, "Обновлённый текст")

    def test_delete_removes_blog_and_redirects(self):
        response = self.client.post(
            reverse("blog_crud:blog_delete", args=[self.blog.pk])
        )

        self.assertRedirects(response, reverse("blog_crud:blog_list"))
        self.assertFalse(Blog.objects.filter(pk=self.blog.pk).exists())

    def test_crud_detail_for_unknown_id_returns_404(self):
        response = self.client.get(reverse("blog_crud:blog_detail", args=[999]))

        self.assertEqual(response.status_code, 404)
