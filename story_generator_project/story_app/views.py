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
    recent_stories = StoryGeneration.objects.all()[:5]  # Show 5 most recent stories
    
    context = {
        'form': form,
        'recent_stories': recent_stories
    }
    return render(request, 'story_app/index.html', context)

@require_http_methods(["POST"])
def generate_story(request):
    """Handle story generation"""
    form = StoryPromptForm(request.POST)
    
    if form.is_valid():
        prompt = form.cleaned_data['prompt']
        length = form.cleaned_data['story_length']
        genre = form.cleaned_data['genre']
        
        try:
            # Initialize story generator service
            story_service = StoryGeneratorService()
            
            # Generate story
            messages.info(request, 'Generating your story... This may take a moment.')
            story = story_service.generate_story(prompt, length, genre)
            
            # Generate character description
            character_description = story_service.generate_character_description(story)
            background_description = story_service.generate_background_description(story)
            
            # Save to database
            story_obj = StoryGeneration.objects.create(
                prompt=prompt,
                generated_story=story,
                character_description=character_description,
                background_description=background_description
            )
            
            messages.success(request, 'Story generated successfully!')
            
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
    """View a specific story"""
    try:
        story_obj = StoryGeneration.objects.get(id=story_id)
        context = {
            'story_obj': story_obj,
        }
        return render(request, 'story_app/story_result.html', context)
    except StoryGeneration.DoesNotExist:
        messages.error(request, 'Story not found.')
        return redirect('index')