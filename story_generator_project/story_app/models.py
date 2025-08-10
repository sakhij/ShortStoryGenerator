from django.db import models
from django.utils import timezone

class StoryGeneration(models.Model):
    prompt = models.TextField(max_length=1000)
    generated_story = models.TextField()
    character_description = models.TextField(blank=True, null=True)
    background_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Story from: {self.prompt[:50]}..."