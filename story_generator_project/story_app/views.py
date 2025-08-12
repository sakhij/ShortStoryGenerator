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
    """Handle complete story generation with character, background, and combined scene images"""
    form = StoryPromptForm(request.POST)
    
    if form.is_valid():
        prompt = form.cleaned_data['prompt']
        length = form.cleaned_data['story_length']
        genre = form.cleaned_data['genre']
        
        try:
            story_service = StoryGeneratorService()
            
            # Generate complete story package with combined scene
            messages.info(request, 'Creating your complete story package with images and combined scene... This may take a few moments.')
            complete_story = story_service.generate_complete_story_with_images(prompt, length, genre)
            logger.info(f"Generated complete story package for prompt: {prompt[:50]}...")
            
            # Extract all image data
            character_image = complete_story.get('character_image', {})
            background_image = complete_story.get('background_image', {})
            combined_scene = complete_story.get('combined_scene', {})
            
            # Save to database with all image sets including combined scene
            story_obj = StoryGeneration.objects.create(
                prompt=prompt,
                generated_story=complete_story['story'],
                character_description=complete_story['character_description'],
                background_description=complete_story['background_description'],
                
                # Character image data
                character_image_data=character_image.get('image_data'),
                character_image_prompt=character_image.get('prompt'),
                character_image_model=character_image.get('model_used'),
                
                # Background image data
                background_image_data=background_image.get('image_data'),
                background_image_prompt=background_image.get('prompt'),
                background_image_model=background_image.get('model_used'),
                
                # NEW: Combined scene data
                combined_scene_data=combined_scene.get('image_data'),
                combined_scene_prompt=combined_scene.get('prompt'),
                combined_scene_model=combined_scene.get('model_used'),
                combination_info=combined_scene.get('composition_info'),
                
                genre=genre,
                story_length=length
            )
            
            # Create comprehensive success message
            success_parts = ['Your complete story']
            
            if character_image.get('success'):
                success_parts.append('character portrait')
            if background_image.get('success'):
                success_parts.append('environment artwork')
            if combined_scene.get('success'):
                success_parts.append('combined scene composition')
            
            # Generate success message based on what was created
            if len(success_parts) > 3:
                success_msg = f"🎉 Complete story package ready! {', '.join(success_parts[:-1])}, and {success_parts[-1]} are all set!"
            elif len(success_parts) > 1:
                success_msg = f"✨ Story package created! {', '.join(success_parts[:-1])}, and {success_parts[-1]} generated successfully!"
            else:
                success_msg = "📖 Your story is ready! (Image generation encountered issues, but the story is complete)"
            
            # Add specific combined scene success info
            if combined_scene.get('success'):
                composition_info = combined_scene.get('composition_info', {})
                char_pos = composition_info.get('char_position', 'center')
                success_msg += f" Character positioned {char_pos} in the scene."
            
            messages.success(request, success_msg)
            
            return render(request, 'story_app/story_result.html', {
                'story_obj': story_obj,
                'prompt': prompt,
                'genre': genre.title(),
                'length': length.title(),
                'image_generation_attempted': True,
                'combined_scene_generated': combined_scene.get('success', False)
            })
            
        except Exception as e:
            logger.error(f"Error generating story with combined scene: {e}")
            messages.error(request, 'Sorry, there was an error generating your story package. Please try again.')
            return redirect('index')
    
    else:
        messages.error(request, 'Please correct the errors in the form.')
        return render(request, 'story_app/index.html', {
            'form': form,
            'recent_stories': StoryGeneration.objects.all()[:5]
        })

def story_detail(request, story_id):
    """View a specific story with all its details including combined scene"""
    try:
        story_obj = StoryGeneration.objects.get(id=story_id)
        return render(request, 'story_app/story_result.html', {
            'story_obj': story_obj,
            'genre': story_obj.genre_display if story_obj.genre else 'Unknown',
            'length': story_obj.story_length.title() if story_obj.story_length else 'Unknown',
            'combined_scene_generated': story_obj.has_combined_scene
        })
    except StoryGeneration.DoesNotExist:
        messages.error(request, 'Story not found.')
        return redirect('index')

def story_list(request):
    """View all generated stories with combined scene indicators"""
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

def download_combined_scene(request, story_id):
    """NEW: Download the combined scene image as a file"""
    try:
        story_obj = StoryGeneration.objects.get(id=story_id)
        if not story_obj.has_combined_scene:
            messages.error(request, 'No combined scene available for this story.')
            return redirect('story_detail', story_id=story_id)
        
        import base64
        from django.http import HttpResponse
        
        # Decode the base64 image
        image_data = base64.b64decode(story_obj.combined_scene_data)
        
        # Create response with proper headers
        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="story_{story_id}_scene.png"'
        
        return response
        
    except StoryGeneration.DoesNotExist:
        messages.error(request, 'Story not found.')
        return redirect('index')
    except Exception as e:
        logger.error(f"Error downloading combined scene: {e}")
        messages.error(request, 'Error downloading image.')
        return redirect('story_detail', story_id=story_id)