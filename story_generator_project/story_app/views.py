from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from .forms import StoryPromptForm
from .models import StoryGeneration
from .services import StoryGeneratorService
import logging
import base64
from django.http import HttpResponse, Http404
from django.utils.encoding import smart_str
import os

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
    """Handle complete story generation with text and/or audio input"""
    form = StoryPromptForm(request.POST, request.FILES)
    
    if form.is_valid():
        text_prompt = form.cleaned_data['prompt']
        audio_file = form.cleaned_data['audio_file']
        input_type = form.cleaned_data['input_type']
        length = form.cleaned_data['story_length']
        genre = form.cleaned_data['genre']
        
        try:
            story_service = StoryGeneratorService()
            
            # Validate audio file if provided
            if audio_file:
                validation_result = story_service.validate_audio_file(audio_file)
                if not validation_result['valid']:
                    messages.error(request, f"Audio validation failed: {validation_result['error']}")
                    return render(request, 'story_app/index.html', {
                        'form': form,
                        'recent_stories': StoryGeneration.objects.all()[:5]
                    })
                
                if validation_result.get('warning'):
                    messages.warning(request, validation_result['warning'])
            
            # Generate story based on input type
            if input_type == 'audio' and audio_file:
                messages.info(request, 'Transcribing audio and creating your complete story package... This may take a few moments.')
                complete_story = story_service.generate_story_from_audio(audio_file, length, genre)
                
            elif input_type == 'both' and (text_prompt or audio_file):
                messages.info(request, 'Processing both text and audio inputs to create your story package... This may take a few moments.')
                complete_story = story_service.generate_story_from_mixed_input(text_prompt, audio_file, length, genre)
                
            else:
                messages.info(request, 'Creating your complete story package with images... This may take a few moments.')
                complete_story = story_service.generate_complete_story_with_images(text_prompt, length, genre)
                complete_story.update({
                    'input_type': 'text',
                    'success': True,
                    'audio_transcription': None,
                    'audio_duration': 0,
                    'transcription_result': None
                })
            
            # Check if story generation was successful
            if not complete_story.get('success', True):
                error_msg = complete_story.get('error', 'Unknown error occurred during story generation')
                messages.error(request, f'Story generation failed: {error_msg}')
                return redirect('index')
            
            logger.info(f"Generated complete story package for input type: {input_type}")
            
            # Extract image data
            character_image = complete_story.get('character_image', {})
            background_image = complete_story.get('background_image', {})
            combined_scene = complete_story.get('combined_scene', {})
            
            # Save audio file if provided
            audio_file_saved = None
            if audio_file:
                try:
                    file_path = default_storage.save(f'audio_prompts/{audio_file.name}', audio_file)
                    audio_file_saved = file_path
                except Exception as e:
                    logger.error(f"Failed to save audio file: {e}")
                    messages.warning(request, "Audio file could not be saved, but transcription was successful.")
            
            # Save to database with all data including audio information
            story_obj = StoryGeneration.objects.create(
                prompt=text_prompt or "",
                generated_story=complete_story['story'],
                character_description=complete_story['character_description'],
                background_description=complete_story['background_description'],
                
                # Audio-related fields
                audio_file=audio_file_saved,
                audio_transcription=complete_story.get('audio_transcription'),
                audio_duration=complete_story.get('audio_duration', 0),
                input_type=complete_story.get('input_type', 'text'),
                
                # Image data
                character_image_data=character_image.get('image_data'),
                character_image_prompt=character_image.get('prompt'),
                character_image_model=character_image.get('model_used'),
                
                # Background image data
                background_image_data=background_image.get('image_data'),
                background_image_prompt=background_image.get('prompt'),
                background_image_model=background_image.get('model_used'),
                
                # Combined scene data
                combined_scene_data=combined_scene.get('image_data'),
                combined_scene_prompt=combined_scene.get('prompt'),
                combined_scene_model=combined_scene.get('model_used'),
                combination_info=combined_scene.get('composition_info'),
                
                genre=genre,
                story_length=length
            )
            
            success_parts = []
            
            if complete_story.get('input_type') == 'audio':
                success_parts.append('audio transcription')
            elif complete_story.get('input_type') == 'both':
                success_parts.append('text + audio processing')
            else:
                success_parts.append('text processing')
            
            # Add generated content info
            success_parts.append('complete story')
            
            if character_image.get('success'):
                success_parts.append('character portrait')
            if background_image.get('success'):
                success_parts.append('environment artwork')
            if combined_scene.get('success'):
                success_parts.append('combined scene composition')
            
            # Generate success message
            if len(success_parts) > 3:
                success_msg = f"Complete story package ready! {', '.join(success_parts[:-1])}, and {success_parts[-1]} are all set!"
            elif len(success_parts) > 1:
                success_msg = f"Story package created! {', '.join(success_parts[:-1])}, and {success_parts[-1]} generated successfully!"
            else:
                success_msg = "Your story is ready! (Image generation encountered issues, but the story is complete)"
            
            # Add audio-specific info
            if complete_story.get('audio_duration', 0) > 0:
                duration_str = f"{complete_story['audio_duration']:.1f} seconds"
                success_msg += f" Audio duration: {duration_str}."
            
            # Add transcription info if available
            transcription_result = complete_story.get('transcription_result', {})
            if transcription_result and transcription_result.get('success'):
                if transcription_result.get('language'):
                    success_msg += f" Detected language: {transcription_result['language']}."
            
            messages.success(request, success_msg)
            
            return render(request, 'story_app/story_result.html', {
                'story_obj': story_obj,
                'prompt': story_obj.effective_prompt,
                'genre': genre.title(),
                'length': length.title(),
                'image_generation_attempted': True,
                'combined_scene_generated': combined_scene.get('success', False),
                'audio_processed': complete_story.get('input_type') in ['audio', 'both'],
                'transcription_result': transcription_result
            })
            
        except Exception as e:
            logger.error(f"Error generating story with audio support: {e}")
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
            'combined_scene_generated': story_obj.has_combined_scene,
            'audio_processed': story_obj.has_audio
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
    
def download_audio_file(request, story_id):
    """Download the original audio file"""
    try:
        story_obj = StoryGeneration.objects.get(id=story_id)
        if not story_obj.has_audio:
            messages.error(request, 'No audio file available for this story.')
            return redirect('story_detail', story_id=story_id)
        
        audio_file = story_obj.audio_file
        if not audio_file or not default_storage.exists(audio_file.name):
            messages.error(request, 'Audio file not found.')
            return redirect('story_detail', story_id=story_id)
        
        # Create response with proper headers
        response = HttpResponse(audio_file.read(), content_type='audio/mpeg')
        filename = os.path.basename(audio_file.name)
        response['Content-Disposition'] = f'attachment; filename="{smart_str(filename)}"'
        
        return response
        
    except StoryGeneration.DoesNotExist:
        messages.error(request, 'Story not found.')
        return redirect('index')
    except Exception as e:
        logger.error(f"Error downloading audio file: {e}")
        messages.error(request, 'Error downloading audio file.')
        return redirect('story_detail', story_id=story_id)