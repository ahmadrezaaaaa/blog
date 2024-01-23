from django.core.cache import cache
from .models import Post
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
def on_posts_changes(sender, instance, **kwargs):
    cache.delete("posts_list")
    cache.delete(f"{instance.id}_retrieve")
