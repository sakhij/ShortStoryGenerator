from django.db import models

class StoryGeneration(models.Model):
    GENRE_CHOICES = [
        ('fantasy', 'Fantasy'),
        ('sci-fi', 'Science Fiction'),
        ('mystery', 'Mystery'),
        ('romance', 'Romance'),
        ('adventure', 'Adventure'),
        ('horror', 'Horror'),
        ('drama', 'Drama'),
        ('comedy', 'Comedy'),
    ]
    
    LENGTH_CHOICES = [
        ('short', 'Short (50-100 words)'),
        ('medium', 'Medium (100-200 words)'),
        ('long', 'Long (200-250 words)'),
    ]
    
    prompt = models.TextField(max_length=1000)
    generated_story = models.TextField()
    character_description = models.TextField(blank=True)
    background_description = models.TextField(blank=True)
    
    # Character image fields
    character_image_data = models.TextField(blank=True, null=True)  # Base64 encoded image
    character_image_prompt = models.TextField(blank=True, null=True)  # Generated prompt
    character_image_model = models.CharField(max_length=100, blank=True, null=True)
    
    # Background image fields
    background_image_data = models.TextField(blank=True, null=True)  # Base64 encoded image
    background_image_prompt = models.TextField(blank=True, null=True)  # Generated prompt
    background_image_model = models.CharField(max_length=100, blank=True, null=True)
    
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='fantasy')
    story_length = models.CharField(max_length=10, choices=LENGTH_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Story: {self.prompt[:50]}..." if len(self.prompt) > 50 else self.prompt
    
    @property
    def genre_display(self):
        return dict(self.GENRE_CHOICES).get(self.genre, 'Unknown')
    
    @property
    def has_character_image(self):
        return bool(self.character_image_data)
    
    @property
    def has_background_image(self):
        return bool(self.background_image_data)
    
    @property
    def character_image_url(self):
        """Return data URL for displaying character image"""
        if self.character_image_data:
            return f"data:image/png;base64,{self.character_image_data}"
        return None
    
    @property
    def background_image_url(self):
        """Return data URL for displaying background image"""
        if self.background_image_data:
            return f"data:image/png;base64,{self.background_image_data}"
        return None