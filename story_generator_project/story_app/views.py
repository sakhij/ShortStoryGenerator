from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .forms import StoryPromptForm
from .models import StoryGeneration
from .services import StoryGeneratorService
import logging
import time

logger = logging.getLogger(__name__)

def index(request):
    """Main page with the story generation form"""
    form = StoryPromptForm()
    recent_stories = StoryGeneration.objects.all()[:5]  # Show 5 most recent stories
    
    context = {
        'form': form,
        'recent_stories': recent_stories
    }
    return render(request, 'story_app/index.html', context)

@require_http_methods(["POST"])
def generate_story(request):
    """Handle story generation with detailed character and background descriptions"""
    form = StoryPromptForm(request.POST)
    
    if form.is_valid():
        prompt = form.cleaned_data['prompt']
        length = form.cleaned_data['story_length']
        genre = form.cleaned_data['genre']
        
        try:
            # Initialize story generator service
            story_service = StoryGeneratorService()
            
            # Step 1: Generate the main story
            messages.info(request, 'Crafting your story... This may take a moment.')
            story = story_service.generate_story(prompt, length, genre)
            logger.info(f"Generated story for prompt: {prompt[:50]}...")
            
            # Step 2: Generate detailed character description
            messages.info(request, 'Creating detailed character profile...')
            character_description = story_service.generate_character_description(story)
            logger.info("Generated character description")
            
            # Step 3: Generate detailed background/world description
            messages.info(request, 'Building the world and setting...')
            background_description = story_service.generate_background_description(story, genre)
            logger.info("Generated background description")
            
            # Save to database with all details
            story_obj = StoryGeneration.objects.create(
                prompt=prompt,
                generated_story=story,
                character_description=character_description,
                background_description=background_description,
                genre=genre,
                story_length=length
            )
            
            messages.success(request, 'Story complete! Your tale, character profile, and world guide are ready!')
            
            context = {
                'story_obj': story_obj,
                'prompt': prompt,
                'genre': genre.title(),
                'length': length.title()
            }
            return render(request, 'story_app/story_result.html', context)
            
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            messages.error(request, 'Sorry, there was an error generating your story. Please try again.')
            return redirect('index')
    
    else:
        messages.error(request, 'Please correct the errors in the form.')
        recent_stories = StoryGeneration.objects.all()[:5]
        context = {
            'form': form,
            'recent_stories': recent_stories
        }
        return render(request, 'story_app/index.html', context)

def story_detail(request, story_id):
    """View a specific story with all its details"""
    try:
        story_obj = StoryGeneration.objects.get(id=story_id)
        context = {
            'story_obj': story_obj,
            'genre': story_obj.genre_display if story_obj.genre else 'Unknown',
            'length': story_obj.story_length.title() if story_obj.story_length else 'Unknown'
        }
        return render(request, 'story_app/story_result.html', context)
    except StoryGeneration.DoesNotExist:
        messages.error(request, 'Story not found.')
        return redirect('index')

def story_list(request):
    """View all generated stories"""
    stories = StoryGeneration.objects.all()[:20]  # Show latest 20 stories
    context = {
        'stories': stories
    }
    return render(request, 'story_app/story_list.html', context)

def delete_story(request, story_id):
    """Delete a specific story (optional feature)"""
    if request.method == 'POST':
        try:
            story_obj = StoryGeneration.objects.get(id=story_id)
            story_obj.delete()
            messages.success(request, 'Story deleted successfully!')
        except StoryGeneration.DoesNotExist:
            messages.error(request, 'Story not found.')
    
    return redirect('index')