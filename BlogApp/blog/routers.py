from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register("posts", PostViewSet, basename="posts")

urlpatterns = router.urls
