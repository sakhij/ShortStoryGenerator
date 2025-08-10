from django.db import models

class StoryGeneration(models.Model):
    prompt = models.TextField(max_length=1000)
    generated_story = models.TextField()
    character_description = models.TextField(blank=True, null=True)
    background_description = models.TextField(blank=True, null=True)  # New field for world/setting
    genre = models.CharField(max_length=50, blank=True, null=True)    # Store genre info
    story_length = models.CharField(max_length=20, blank=True, null=True)  # Store length info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Story Generation"
        verbose_name_plural = "Story Generations"
    
    def __str__(self):
        return f"Story: {self.prompt[:50]}..."
    
    def get_absolute_url(self):
        return f"/story/{self.id}/"
    
    @property
    def word_count(self):
        """Return approximate word count of the generated story"""
        return len(self.generated_story.split())
    
    @property
    def genre_display(self):
        """Return formatted genre name"""
        return self.genre.replace('-', ' ').title() if self.genre else 'Unknown'