from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "BlogApp.blog"

    def ready(self):
        import BlogApp.blog.signals
