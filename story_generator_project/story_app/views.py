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
    """Handle complete story generation with character and background images using multiple chains"""
    form = StoryPromptForm(request.POST)
    
    if form.is_valid():
        prompt = form.cleaned_data['prompt']
        length = form.cleaned_data['story_length']
        genre = form.cleaned_data['genre']
        
        try:
            story_service = StoryGeneratorService()
            
            # Generate complete story package with both images
            messages.info(request, 'Creating your complete story package with images... This may take a few moments.')
            complete_story = story_service.generate_complete_story_with_images(prompt, length, genre)
            logger.info(f"Generated complete story package for prompt: {prompt[:50]}...")
            
            # Extract image data
            character_image = complete_story.get('character_image', {})
            background_image = complete_story.get('background_image', {})
            
            # Save to database with both image sets
            story_obj = StoryGeneration.objects.create(
                prompt=prompt,
                generated_story=complete_story['story'],
                character_description=complete_story['character_description'],
                background_description=complete_story['background_description'],
                character_image_data=character_image.get('image_data'),
                character_image_prompt=character_image.get('prompt'),
                character_image_model=character_image.get('model_used'),
                background_image_data=background_image.get('image_data'),
                background_image_prompt=background_image.get('prompt'),
                background_image_model=background_image.get('model_used'),
                genre=genre,
                story_length=length
            )
            
            # Create success message based on what was generated
            success_parts = ['Your tale, character profile, and world guide']
            if character_image.get('success'):
                success_parts.append('character portrait')
            if background_image.get('success'):
                success_parts.append('environment artwork')
            
            if len(success_parts) > 1:
                success_msg = f"Complete story package ready! {', '.join(success_parts[:-1])}, and {success_parts[-1]} are all set!"
            else:
                success_msg = f"{success_parts[0]} are ready! (Image generation failed, but story is complete)"
            
            messages.success(request, success_msg)
            
            return render(request, 'story_app/story_result.html', {
                'story_obj': story_obj,
                'prompt': prompt,
                'genre': genre.title(),
                'length': length.title(),
                'image_generation_attempted': True
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