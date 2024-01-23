from .models import Post
from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import PostSerializer
from .tasks import add


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
        invalid_data = [{'title': '', 'content': 'content'},
                        {'title': 'title', 'content': '', }]
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
    base_url = '/api/'

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test', is_superuser=True)
        data = {"username": "test", "password": "test"}
        login_res = self.client.post(self.base_url + 'token/', data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + login_res.data['access'])

    @staticmethod
    def create_post():
        return Post.objects.create(title="title", content="content")

    def test_post_create(self):
        # create a post
        payload = {"title": "title", "content": "content"}
        res = self.client.post(self.base_url + 'posts/', payload)
        _id = res.data['id']
        self.assertEquals(res.status_code, status.HTTP_201_CREATED)

        # check if the post is created
        self.assertTrue(Post.objects.get(id=_id, title=payload["title"], content=payload["content"]))

    def test_post_update(self):
        # create one post
        new_post = self.create_post()

        # update the post
        payload = {"title": "title", "content": "new content"}
        res = self.client.put(self.base_url + f'posts/{new_post.id}/', payload)
        updated_post = Post.objects.get(pk=new_post.id)
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(updated_post.content, payload['content'])

    def test_post_list(self):
        # create the post
        new_post = self.create_post()

        # get the post list
        res = self.client.get(self.base_url + 'posts/')
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(len(res.data), 1)
        self.assertEquals(res.data[0]['title'], new_post.title)
        self.assertEquals(res.data[0]['content'], new_post.content)

    def test_post_get(self):
        # create one post
        new_post = self.create_post()

        # get a specific post  list
        res = self.client.get(self.base_url + f'posts/{new_post.id}/')
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data['title'], new_post.title)
        self.assertEquals(res.data['content'], new_post.content)

    def test_post_add_task(self):
        # test the task endpoint
        res = self.client.get(self.base_url + 'posts/run_celery_task/')
        self.assertEquals(res.status_code, status.HTTP_200_OK)

        # check if the task has been run
        self.assertIn(res.data['task_status'], ['PENDING', 'STARTED', 'SUCCESS'])
