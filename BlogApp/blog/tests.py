from django.core.cache import cache
from .models import Post
from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from rest_framework import status
from django.contrib.auth.models import User, Permission
from .serializers import PostSerializer
from .tasks import add


class PostPermissionsTest(APITestCase):
    client = APIClient(enforce_csrf_checks=True)
    base_url = "/api/"

    def setUp(self):
        # create a simple user with no permission
        self.user = User.objects.create_user(
            username="test", password="test", is_superuser=False
        )
        data = {"username": "test", "password": "test"}
        login_res = self.client.post(self.base_url + "token/", data, format="json")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login_res.data["access"])

    @staticmethod
    def create_post():
        return Post.objects.create(title="title", content="content")

    def test_post_create(self):
        # create a post
        payload = {"title": "title", "content": "content"}
        res = self.client.post(self.base_url + "posts/", payload)
        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            Post.objects.filter(
                title=payload["title"], content=payload["content"]
            ).exists()
        )

        # give th add permission to user
        permission = Permission.objects.get(codename="add_post")
        self.user.user_permissions.add(permission)

        # test again
        payload = {"title": "title", "content": "content"}
        res = self.client.post(self.base_url + "posts/", payload)
        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Post.objects.filter(
                title=payload["title"], content=payload["content"]
            ).exists()
        )

    def test_post_update(self):
        # create a post
        new_post = self.create_post()

        # try update it
        payload = {"title": "title", "content": "new content"}
        res = self.client.put(self.base_url + f"posts/{new_post.id}/", payload)
        updated_post = Post.objects.get(pk=new_post.id)
        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEquals(updated_post.content, payload["content"])

        # give th add permission to user
        permission = Permission.objects.get(codename="change_post")
        self.user.user_permissions.add(permission)

        # test again
        payload = {"title": "title", "content": "new content"}
        res = self.client.put(self.base_url + f"posts/{new_post.id}/", payload)
        updated_post = Post.objects.get(pk=new_post.id)
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(updated_post.content, payload["content"])

    def test_post_list(self):
        # create a post
        new_post = self.create_post()

        # try get it
        res = self.client.get(self.base_url + "posts/")
        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)

        # give th add permission to user
        permission = Permission.objects.get(codename="view_post")
        self.user.user_permissions.add(permission)

        # test again
        res = self.client.get(self.base_url + "posts/")
        self.assertEquals(res.status_code, status.HTTP_200_OK)

    def test_post_delete(self):
        # create a post
        new_post = self.create_post()

        # try delete it
        res = self.client.delete(self.base_url + f"posts/{new_post.id}/")
        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(id=new_post.id).exists())

        # give th add permission to user
        permission = Permission.objects.get(codename="delete_post")
        self.user.user_permissions.add(permission)

        # test again
        res = self.client.delete(self.base_url + f"posts/{new_post.id}/")
        self.assertEquals(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=new_post.id).exists())


class PostTasksTest(TestCase):
    def test_add_function(self):
        # test functionality of the add function
        result = add(5, 5)
        self.assertEquals(result, 10)

    def test_add_task(self):
        # test functionality of the add function as a task
        result = add.delay(5, 5).get()
        self.assertEquals(result, 10)


class PostSerializersTest(TestCase):
    def test_required_fields(self):
        invalid_data = [
            {"title": "", "content": "content"},
            {
                "title": "title",
                "content": "",
            },
        ]
        for data in invalid_data:
            serialized = PostSerializer(data=data)
            self.assertFalse(serialized.is_valid())

    def test_returned_fields(self):
        # create the post
        post_data = {"title": "title", "content": "content"}
        post = Post.objects.create(**post_data)

        # serialize the instance
        serialized = PostSerializer(instance=post)
        all_fields = [field.name for field in Post._meta.get_fields()]
        self.assertEquals(list(serialized.data.keys()), all_fields)


class PostEndpointsTest(APITestCase):
    client = APIClient(enforce_csrf_checks=True)
    base_url = "/api/"

    def setUp(self):
        self.user = User.objects.create_user(
            username="test", password="test", is_superuser=True
        )
        data = {"username": "test", "password": "test"}
        login_res = self.client.post(self.base_url + "token/", data, format="json")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login_res.data["access"])

    @staticmethod
    def create_post():
        return Post.objects.create(title="title", content="content")

    def test_post_create(self):
        # create a post
        payload = {"title": "title", "content": "content"}
        res = self.client.post(self.base_url + "posts/", payload)
        _id = res.data["id"]
        self.assertEquals(res.status_code, status.HTTP_201_CREATED)

        # check if the post is created
        self.assertTrue(
            Post.objects.get(id=_id, title=payload["title"], content=payload["content"])
        )

    def test_post_update(self):
        # create one post
        new_post = self.create_post()

        # update the post
        payload = {"title": "title", "content": "new content"}
        res = self.client.put(self.base_url + f"posts/{new_post.id}/", payload)
        updated_post = Post.objects.get(pk=new_post.id)
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(updated_post.content, payload["content"])

    def test_post_list(self):
        # create the post
        new_post = self.create_post()

        # get the posts list
        res = self.client.get(self.base_url + "posts/")
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(len(res.data), 1)
        self.assertEquals(res.data[0]["title"], new_post.title)
        self.assertEquals(res.data[0]["content"], new_post.content)

    def test_post_get(self):
        # create one post
        new_post = self.create_post()

        # get a specific post
        res = self.client.get(self.base_url + f"posts/{new_post.id}/")
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data["title"], new_post.title)
        self.assertEquals(res.data["content"], new_post.content)

    def test_post_delete(self):
        # create a post
        new_post = self.create_post()

        # delete and check if has been deleted
        res = self.client.delete(self.base_url + f"posts/{new_post.id}/")
        self.assertEquals(res.status_code, status.HTTP_204_NO_CONTENT)
        new_post = Post.objects.filter(id=new_post.id).exists()
        self.assertFalse(new_post)

    def test_post_add_task(self):
        # test the task endpoint
        res = self.client.get(self.base_url + "posts/run_celery_task/")
        self.assertEquals(res.status_code, status.HTTP_200_OK)

        # check if the task has been run
        self.assertIn(res.data["task_status"], ["PENDING", "STARTED", "SUCCESS"])


class PostCachesTest(APITestCase):
    client = APIClient(enforce_csrf_checks=True)
    base_url = "/api/"

    def setUp(self):
        self.user = User.objects.create_user(
            username="test", password="test", is_superuser=True
        )
        data = {"username": "test", "password": "test"}
        login_res = self.client.post(self.base_url + "token/", data, format="json")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login_res.data["access"])

    @staticmethod
    def create_post():
        return Post.objects.create(title="title", content="content")

    def test_post_list_caching(self):
        # create the post
        self.create_post()

        # get the posts list
        self.client.get(self.base_url + "posts/")
        self.assertNotEquals(cache.get("posts_list"), None)

    def test_delete_post_list_caching_on_save(self):
        # create the post
        self.create_post()

        # get the posts list
        self.client.get(self.base_url + "posts/")
        self.assertNotEquals(cache.get("posts_list"), None)

        # create a new posts to delete old cache
        payload = {"title": "title2", "content": "content2"}
        self.client.post(self.base_url + "posts/", payload)
        self.assertEquals(cache.get("posts_list"), None)

    def test_delete_post_list_caching_on_delete(self):
        # create the post
        new_post = self.create_post()

        # check the posts cache
        self.client.get(self.base_url + "posts/")
        self.assertNotEquals(cache.get("posts_list"), None)

        # delete the created post to check the data freshness
        self.client.delete(self.base_url + f"posts/{new_post.id}/")
        self.assertEquals(cache.get("posts_list"), None)

    def test_post_retrieve_caching(self):
        # create the post
        new_post = self.create_post()

        # get the posts list
        self.client.get(self.base_url + f"posts/{new_post.id}/")
        self.assertNotEquals(cache.get(f"{new_post.id}_retrieve"), None)

    def test_delete_post_retrieve_caching_on_delete(self):
        # create the post
        new_post = self.create_post()

        # get the posts list
        self.client.get(self.base_url + f"posts/{new_post.id}/")
        self.assertNotEquals(cache.get(f"{new_post.id}_retrieve"), None)

        # delete the record to test if the cache has been deleted
        self.client.delete(self.base_url + f"posts/{new_post.id}/")
        self.assertEquals(cache.get(f"{new_post.id}_retrieve"), None)

    def test_delete_post_retrieve_caching_on_update(self):
        # create the post
        new_post = self.create_post()

        # get the posts list
        self.client.get(self.base_url + f"posts/{new_post.id}/")
        self.assertNotEquals(cache.get(f"{new_post.id}_retrieve"), None)

        #  update to test if the cache has been deleted
        payload = {"title": "title", "content": "new content"}
        self.client.put(self.base_url + f"posts/{new_post.id}/", payload)
        self.assertEquals(cache.get(f"{new_post.id}_retrieve"), None)
