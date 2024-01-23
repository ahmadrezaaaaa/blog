from django.core.cache import cache
from rest_framework.decorators import action
from .models import Post
from rest_framework.viewsets import ModelViewSet
from .serializers import PostSerializer
from .tasks import add
from rest_framework.response import Response


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def list(self, request, *args, **kwargs):
        cached_posts_list = cache.get("posts_list")
        if cached_posts_list:
            return Response(cached_posts_list)

        cached_posts_list = super().list(request, *args, **kwargs)
        cache.set("posts_list", cached_posts_list.data)
        return cached_posts_list

    def retrieve(self, request, *args, **kwargs):
        item_id = kwargs.get("pk")
        cache_key = f"{item_id}_retrieve"
        cached_post = cache.get(cache_key)

        if cached_post:
            return Response(cached_post)

        cached_post = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, cached_post.data)
        return cached_post

    @action(methods=["get"], detail=False)
    def run_celery_task(self, request):
        task_result = add.delay(4, 4)
        return Response({"task_status": task_result.status})
