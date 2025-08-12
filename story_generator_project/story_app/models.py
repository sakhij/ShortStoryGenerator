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
    
    # NEW: Combined scene image fields
    combined_scene_data = models.TextField(blank=True, null=True)  # Base64 encoded combined image
    combined_scene_prompt = models.TextField(blank=True, null=True)  # Description of combination
    combined_scene_model = models.CharField(max_length=100, blank=True, null=True)  # Compositor used
    combination_info = models.JSONField(blank=True, null=True)  # Position and composition data
    
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
    def has_combined_scene(self):
        """NEW: Check if combined scene image exists"""
        return bool(self.combined_scene_data)
    
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
    
    @property
    def combined_scene_url(self):
        """NEW: Return data URL for displaying combined scene image"""
        if self.combined_scene_data:
            return f"data:image/png;base64,{self.combined_scene_data}"
        return None
    
    @property
    def has_complete_image_set(self):
        """Check if all three image types are available"""
        return (self.has_character_image and 
                self.has_background_image and 
                self.has_combined_scene)
    
    @property
    def image_generation_summary(self):
        """Get summary of image generation results"""
        summary = []
        if self.has_character_image:
            summary.append("Character Portrait")
        if self.has_background_image:
            summary.append("Environment Art")
        if self.has_combined_scene:
            summary.append("Combined Scene")
        
        return summary
    
    @property
    def composition_summary(self):
        """Get human-readable composition information"""
        if self.combination_info:
            info = self.combination_info
            position = info.get('char_position', 'center')
            size = info.get('char_size_factor', 0.6)
            interaction = info.get('interaction_type', 'standing')
            
            size_desc = "small" if size < 0.5 else "large" if size > 0.7 else "medium"
            return f"Character positioned {position}, {size_desc} size, {interaction} pose"
        return "No composition data available"