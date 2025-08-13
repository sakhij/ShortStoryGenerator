# models.py - Enhanced with audio support
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
    
    INPUT_TYPE_CHOICES = [
        ('text', 'Text Only'),
        ('audio', 'Audio Only'),
        ('both', 'Text + Audio'),
    ]
    
    # Original fields
    prompt = models.TextField(max_length=1000, blank=True)  # Now optional
    generated_story = models.TextField()
    character_description = models.TextField(blank=True)
    background_description = models.TextField(blank=True)
    
    # Audio-related fields
    audio_file = models.FileField(upload_to='audio_prompts/', blank=True, null=True)
    audio_transcription = models.TextField(blank=True, null=True)  # Store transcribed text
    audio_duration = models.FloatField(blank=True, null=True)  # Duration in seconds
    input_type = models.CharField(max_length=10, choices=INPUT_TYPE_CHOICES, default='text')
    
    # Image fields (existing)
    character_image_data = models.TextField(blank=True, null=True)
    character_image_prompt = models.TextField(blank=True, null=True)
    character_image_model = models.CharField(max_length=100, blank=True, null=True)
    
    background_image_data = models.TextField(blank=True, null=True)
    background_image_prompt = models.TextField(blank=True, null=True)
    background_image_model = models.CharField(max_length=100, blank=True, null=True)
    
    combined_scene_data = models.TextField(blank=True, null=True)
    combined_scene_prompt = models.TextField(blank=True, null=True)
    combined_scene_model = models.CharField(max_length=100, blank=True, null=True)
    combination_info = models.JSONField(blank=True, null=True)
    
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='fantasy')
    story_length = models.CharField(max_length=10, choices=LENGTH_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.input_type == 'audio' and self.audio_transcription:
            display_text = self.audio_transcription[:50]
        elif self.prompt:
            display_text = self.prompt[:50]
        else:
            display_text = "Audio Story"
        
        return f"Story: {display_text}..." if len(display_text) > 45 else f"Story: {display_text}"
    
    @property
    def effective_prompt(self):
        """Return the effective prompt text (transcribed audio or text prompt)"""
        if self.input_type == 'audio' and self.audio_transcription:
            return self.audio_transcription
        elif self.input_type == 'both':
            combined = []
            if self.prompt:
                combined.append(f"Text: {self.prompt}")
            if self.audio_transcription:
                combined.append(f"Audio: {self.audio_transcription}")
            return " | ".join(combined)
        else:
            return self.prompt or "No prompt available"
    
    @property
    def has_audio(self):
        """Check if story was generated from audio input"""
        return bool(self.audio_file and self.audio_transcription)
    
    @property
    def audio_file_url(self):
        """Return URL for audio file if it exists"""
        if self.audio_file:
            return self.audio_file.url
        return None
    
    @property
    def input_type_display(self):
        return dict(self.INPUT_TYPE_CHOICES).get(self.input_type, 'Unknown')
    
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
        """Check if combined scene image exists"""
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
        """Return data URL for displaying combined scene image"""
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