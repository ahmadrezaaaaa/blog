from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .serializers import PostSerializer
from .tasks import add
from celery.exceptions import OperationalError


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(methods=['get'], detail=False)
    def run_celery_task(self, request):
        task_result = add.delay(4, 4)
        return Response({'task_status': task_result.status})
