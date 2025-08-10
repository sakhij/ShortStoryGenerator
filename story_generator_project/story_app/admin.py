from django.contrib import admin
from .models import StoryGeneration

@admin.register(StoryGeneration)
class StoryGenerationAdmin(admin.ModelAdmin):
    list_display = ['prompt_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['prompt', 'generated_story']
    readonly_fields = ['created_at']
    
    def prompt_preview(self, obj):
        return obj.prompt[:100] + "..." if len(obj.prompt) > 100 else obj.prompt
    prompt_preview.short_description = 'Prompt'