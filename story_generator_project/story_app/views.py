from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import StoryPromptForm
from .models import StoryGeneration
from .services import StoryGeneratorService
import logging

logger = logging.getLogger(__name__)

def index(request):
    """Main page with the story generation form"""
    form = StoryPromptForm()
    recent_stories = StoryGeneration.objects.all()[:5]
    return render(request, 'story_app/index.html', {
        'form': form,
        'recent_stories': recent_stories
    })

@require_http_methods(["POST"])
def generate_story(request):
    """Handle story generation with detailed character and background descriptions"""
    form = StoryPromptForm(request.POST)
    
    if form.is_valid():
        prompt = form.cleaned_data['prompt']
        length = form.cleaned_data['story_length']
        genre = form.cleaned_data['genre']
        
        try:
            story_service = StoryGeneratorService()
            
            # Generate main story
            story = story_service.generate_story(prompt, length, genre)
            logger.info(f"Generated story for prompt: {prompt[:50]}...")
            
            # Generate character and background descriptions
            character_description = story_service.generate_character_description(story)
            background_description = story_service.generate_background_description(story, genre)
            
            # Save to database
            story_obj = StoryGeneration.objects.create(
                prompt=prompt,
                generated_story=story,
                character_description=character_description,
                background_description=background_description,
                genre=genre,
                story_length=length
            )
            
            messages.success(request, 'Story complete! Your tale, character profile, and world guide are ready!')
            
            return render(request, 'story_app/story_result.html', {
                'story_obj': story_obj,
                'prompt': prompt,
                'genre': genre.title(),
                'length': length.title()
            })
            
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            messages.error(request, 'Sorry, there was an error generating your story. Please try again.')
            return redirect('index')
    
    else:
        messages.error(request, 'Please correct the errors in the form.')
        return render(request, 'story_app/index.html', {
            'form': form,
            'recent_stories': StoryGeneration.objects.all()[:5]
        })

def story_detail(request, story_id):
    """View a specific story with all its details"""
    try:
        story_obj = StoryGeneration.objects.get(id=story_id)
        return render(request, 'story_app/story_result.html', {
            'story_obj': story_obj,
            'genre': story_obj.genre_display if story_obj.genre else 'Unknown',
            'length': story_obj.story_length.title() if story_obj.story_length else 'Unknown'
        })
    except StoryGeneration.DoesNotExist:
        messages.error(request, 'Story not found.')
        return redirect('index')

def story_list(request):
    """View all generated stories"""
    stories = StoryGeneration.objects.all()[:20]
    return render(request, 'story_app/story_list.html', {'stories': stories})

def delete_story(request, story_id):
    """Delete a specific story"""
    if request.method == 'POST':
        try:
            story_obj = StoryGeneration.objects.get(id=story_id)
            story_obj.delete()
            messages.success(request, 'Story deleted successfully!')
        except StoryGeneration.DoesNotExist:
            messages.error(request, 'Story not found.')
    
    return redirect('index')