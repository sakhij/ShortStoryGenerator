from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from dotenv import load_dotenv
import logging
import re
import requests
import base64
from io import BytesIO
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import cv2
import numpy as np
import time
import os
from rembg import remove
import whisper
import tempfile
from pydub import AudioSegment

logger = logging.getLogger(__name__)
load_dotenv()

class StoryGeneratorService:
    def __init__(self):
        try:
            self.llm = OllamaLLM(model="gemma:2b")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            self.llm = None
        
        self.hf_image_models = [
            "black-forest-labs/FLUX.1-schnell",
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5",
            "CompVis/stable-diffusion-v1-4"
        ]
        
        hf_token = os.getenv('HUGGINGFACE_TOKEN', 'abc')
        self.hf_headers = {
            "Authorization": f"Bearer {hf_token}"
        }

        self.stability_api_key = os.getenv('STABILITY_API_KEY', '')
        self.stability_headers = {
            "Authorization": f"Bearer {self.stability_api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.stability_url_map = {
            "portrait": "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            "landscape": "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        }

        try:
            self.whisper_model = whisper.load_model("base") 
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.whisper_model = None
    
    def transcribe_audio(self, audio_file):
        """
        Transcribe audio file to text using OpenAI Whisper
        Returns dict with transcription, duration, and metadata
        """
        if not self.whisper_model:
            logger.error("Whisper model not available")
            return {
                'transcription': None,
                'duration': 0,
                'success': False,
                'error': 'Audio transcription service unavailable'
            }
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                # Read the uploaded file content
                audio_file.seek(0)
                file_content = audio_file.read()
                
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                try:
                    audio = AudioSegment.from_file(temp_file_path)
                    duration = len(audio) / 1000.0
                    
                    if not temp_file_path.endswith('.wav'):
                        wav_path = temp_file_path.replace(temp_file_path.split('.')[-1], 'wav')
                        audio.export(wav_path, format="wav")
                        temp_file_path = wav_path
                    
                except Exception as e:
                    logger.warning(f"Audio conversion failed, trying direct transcription: {e}")
                    duration = 0
                
                # Transcribe using Whisper
                logger.info(f"Transcribing audio file: {temp_file_path}")
                result = self.whisper_model.transcribe(temp_file_path)
                transcription = result["text"].strip()
                
                logger.info(f"Audio transcription successful: {transcription[:100]}...")
                
                return {
                    'transcription': transcription,
                    'duration': duration,
                    'success': True,
                    'language': result.get('language', 'unknown'),
                    'segments': len(result.get('segments', []))
                }
                
            finally:
                try:
                    os.unlink(temp_file_path)
                    if 'wav_path' in locals() and wav_path != temp_file_path:
                        os.unlink(wav_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {
                'transcription': None,
                'duration': 0,
                'success': False,
                'error': str(e)
            }
    def generate_story_from_audio(self, audio_file, length='medium', genre='fantasy'):
        """
        Complete pipeline: transcribe audio -> generate story with images
        """
        try:
            # Step 1: Transcribe audio
            logger.info("Starting audio transcription...")
            transcription_result = self.transcribe_audio(audio_file)
            
            if not transcription_result['success']:
                return {
                    'success': False,
                    'error': transcription_result.get('error', 'Audio transcription failed'),
                    'transcription_result': transcription_result
                }
            
            transcription = transcription_result['transcription']
            
            if not transcription or len(transcription.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Audio transcription too short or empty',
                    'transcription_result': transcription_result
                }
            
            logger.info(f"Audio transcribed successfully: {len(transcription)} characters")
            
            # Step 2: Generate story using transcription as prompt
            logger.info("Generating story from transcription...")
            story_package = self.generate_complete_story_with_images(
                prompt=transcription,
                length=length,
                genre=genre
            )
            
            # Add transcription metadata to the package
            story_package.update({
                'transcription_result': transcription_result,
                'audio_transcription': transcription,
                'audio_duration': transcription_result['duration'],
                'input_type': 'audio',
                'success': True
            })
            
            return story_package
            
        except Exception as e:
            logger.error(f"Error in audio story generation pipeline: {e}")
            return {
                'success': False,
                'error': str(e),
                'transcription_result': None
            }
    
    def generate_story_from_mixed_input(self, text_prompt=None, audio_file=None, length='medium', genre='fantasy'):
        """
        Generate story from both text and audio inputs
        """
        try:
            combined_prompt_parts = []
            transcription_result = None
            audio_duration = 0
            
            if text_prompt and text_prompt.strip():
                combined_prompt_parts.append(f"Text prompt: {text_prompt}")
            
            if audio_file:
                logger.info("Transcribing audio for mixed input...")
                transcription_result = self.transcribe_audio(audio_file)
                
                if transcription_result['success']:
                    audio_duration = transcription_result['duration']
                    combined_prompt_parts.append(f"Audio description: {transcription_result['transcription']}")
                else:
                    logger.warning(f"Audio transcription failed: {transcription_result.get('error')}")
            
            if not combined_prompt_parts:
                return {
                    'success': False,
                    'error': 'No valid input provided (text or audio)',
                    'transcription_result': transcription_result
                }
            
            # Combine all inputs into a single prompt
            combined_prompt = " | ".join(combined_prompt_parts)
            
            # Generate story using combined prompt
            logger.info("Generating story from mixed input...")
            story_package = self.generate_complete_story_with_images(
                prompt=combined_prompt,
                length=length,
                genre=genre
            )
            
            # Add metadata
            story_package.update({
                'transcription_result': transcription_result,
                'audio_transcription': transcription_result['transcription'] if transcription_result and transcription_result['success'] else None,
                'audio_duration': audio_duration,
                'input_type': 'both',
                'combined_prompt': combined_prompt,
                'success': True
            })
            
            return story_package
            
        except Exception as e:
            logger.error(f"Error in mixed input story generation: {e}")
            return {
                'success': False,
                'error': str(e),
                'transcription_result': transcription_result
            }

    def validate_audio_file(self, audio_file):
        """Validate uploaded audio file"""
        allowed_formats = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac']
        max_size = 10 * 1024 * 1024 
        max_duration = 300
        
        try:
            if audio_file.size > max_size:
                return {
                    'valid': False,
                    'error': f'File too large. Maximum size is {max_size / (1024*1024):.1f}MB'
                }
            
            file_ext = os.path.splitext(audio_file.name.lower())[1]
            if file_ext not in allowed_formats:
                return {
                    'valid': False,
                    'error': f'Unsupported format. Allowed formats: {", ".join(allowed_formats)}'
                }
            
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    audio_file.seek(0)
                    temp_file.write(audio_file.read())
                    temp_file_path = temp_file.name
                
                audio = AudioSegment.from_file(temp_file_path)
                duration = len(audio) / 1000.0
                
                os.unlink(temp_file_path)
                
                if duration > max_duration:
                    return {
                        'valid': False,
                        'error': f'Audio too long. Maximum duration is {max_duration/60:.1f} minutes'
                    }
                
                return {
                    'valid': True,
                    'duration': duration,
                    'format': file_ext
                }
                
            except Exception as e:
                logger.warning(f"Could not validate audio duration: {e}")
                return {
                    'valid': True,
                    'duration': 0,
                    'format': file_ext,
                    'warning': 'Could not validate audio duration'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error validating audio file: {str(e)}'
            }
        

    def generate_complete_story_with_images(self, prompt, length='medium', genre='fantasy'):
        """Generate story, character description, background description, character image, and background image"""
        
        # First generate the complete story package
        story_package = self.generate_complete_story(prompt, length, genre)
        
        # Extract visual style consistency parameters from genre
        visual_style = self._get_visual_style_for_genre(genre)

        # Generate character and background images separately
        character_image_result = None
        background_image_result = None
        
        # Then generate character image based on character description
        if story_package['character_description']:
            try:
                logger.info("Generating character image...")
                character_image_result = self.generate_character_image(
                    story_package['character_description'], 
                    visual_style=visual_style,
                    genre=genre
                )
                story_package['character_image'] = character_image_result
            except Exception as e:
                logger.error(f"Failed to generate character image: {e}")
                story_package['character_image'] = self._generate_placeholder_image("character")
        else:
            story_package['character_image'] = self._generate_placeholder_image("character")
        
        # Generate background image based on background description
        if story_package['background_description']:
            try:
                logger.info("Generating background image...")
                background_image_result = self.generate_background_image(
                    story_package['background_description'],
                    story_package['story'],
                    visual_style=visual_style,
                    genre=genre
                )
                story_package['background_image'] = background_image_result
            except Exception as e:
                logger.error(f"Failed to generate background image: {e}")
                story_package['background_image'] = self._generate_placeholder_image("background")
        else:
            story_package['background_image'] = self._generate_placeholder_image("background")
        
        # Combine character and background into a cohesive scene
        if (character_image_result and character_image_result.get('success') and 
            background_image_result and background_image_result.get('success')):
            try:
                logger.info("Combining images into cohesive scene...")
                combined_image_result = self.combine_images_into_scene(
                    character_image_result['image_data'],
                    background_image_result['image_data'],
                    story_package['character_description'],
                    story_package['background_description'],
                    genre
                )
                story_package['combined_scene'] = combined_image_result
            except Exception as e:
                logger.error(f"Failed to combine images: {e}")
                story_package['combined_scene'] = self._generate_placeholder_image("combined_scene")
        else:
            story_package['combined_scene'] = self._generate_placeholder_image("combined_scene")
        
        return story_package
    
    def combine_images_into_scene(self, character_b64, background_b64, character_desc, background_desc, genre):
        """
        Combine character and background images into a coherent scene using PIL and OpenCV
        NEW METHOD - Core image combination functionality
        """
        try:
            # Decode base64 images
            char_img = self._decode_base64_image(character_b64)
            bg_img = self._decode_base64_image(background_b64)
            
            if char_img is None or bg_img is None:
                raise ValueError("Failed to decode input images")
            
            # Step 1: Analyze and match style/lighting
            char_img, bg_img = self._match_image_styles(char_img, bg_img, genre)
            
            # Step 2: Determine optimal positioning based on descriptions
            position_info = self._analyze_positioning(character_desc, background_desc)
            
            # Step 3: Prepare character (remove background, adjust size)
            char_img_prepared = self._prepare_character_for_composition(char_img, position_info)
            
            # Step 4: Prepare background (adjust for character placement)
            bg_img_prepared = self._prepare_background_for_composition(bg_img, position_info)
            
            # Step 5: Composite the final scene
            combined_image = self._composite_final_scene(char_img_prepared, bg_img_prepared, position_info)
            
            # Step 6: Apply final post-processing
            final_image = self._apply_scene_post_processing(combined_image, genre)
            
            # Convert to base64 for storage
            combined_b64 = self._encode_image_to_base64(final_image)
            
            return {
                'image_data': combined_b64,
                'prompt': f"Combined scene: character in {genre} setting",
                'model_used': 'PIL+OpenCV_compositor',
                'success': True,
                'type': 'combined_scene',
                'composition_info': position_info
            }
            
        except Exception as e:
            logger.error(f"Error combining images: {e}")
            return self._generate_placeholder_image("combined_scene")
    
    def _decode_base64_image(self, base64_str):
        """Convert base64 string to PIL Image"""
        try:
            img_data = base64.b64decode(base64_str)
            img = Image.open(BytesIO(img_data)).convert('RGBA')
            return img
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {e}")
            return None
    
    def _encode_image_to_base64(self, pil_image):
        """Convert PIL Image to base64 string"""
        try:
            buffered = BytesIO()
            pil_image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            return img_base64
        except Exception as e:
            logger.error(f"Failed to encode image to base64: {e}")
            return None
    
    def _match_image_styles(self, char_img, bg_img, genre):
        """
        Match lighting, color temperature, and contrast between character and background
        Uses PIL for color/lighting adjustments
        """
        try:
            # Convert to numpy for analysis
            char_array = np.array(char_img.convert('RGB'))
            bg_array = np.array(bg_img.convert('RGB'))
            
            # Analyze color temperature and lighting
            char_temp = self._calculate_color_temperature(char_array)
            bg_temp = self._calculate_color_temperature(bg_array)
            
            # Analyze brightness and contrast
            char_brightness = np.mean(char_array)
            bg_brightness = np.mean(bg_array)
            
            # Adjust character to match background style
            if abs(char_temp - bg_temp) > 500:  # Significant temperature difference
                char_img = self._adjust_color_temperature(char_img, bg_temp - char_temp)
            
            if abs(char_brightness - bg_brightness) > 20:  # Significant brightness difference
                brightness_factor = bg_brightness / char_brightness if char_brightness > 0 else 1.0
                brightness_factor = max(0.5, min(2.0, brightness_factor))  # Limit adjustment
                enhancer = ImageEnhance.Brightness(char_img)
                char_img = enhancer.enhance(brightness_factor)
            
            # Match contrast levels
            char_contrast = np.std(char_array)
            bg_contrast = np.std(bg_array)
            
            if char_contrast > 0:
                contrast_factor = bg_contrast / char_contrast
                contrast_factor = max(0.7, min(1.5, contrast_factor))
                enhancer = ImageEnhance.Contrast(char_img)
                char_img = enhancer.enhance(contrast_factor)
            
            return char_img, bg_img
            
        except Exception as e:
            logger.error(f"Error matching image styles: {e}")
            return char_img, bg_img
    
    def _calculate_color_temperature(self, img_array):
        """Estimate color temperature of an image"""
        try:
            r_avg = np.mean(img_array[:, :, 0])
            g_avg = np.mean(img_array[:, :, 1])
            b_avg = np.mean(img_array[:, :, 2])
            
            # Simple color temperature estimation
            if b_avg > r_avg:
                return 6500 + (b_avg - r_avg) * 20
            else:
                return 3200 + (r_avg - b_avg) * 20
        except:
            return 5500
    
    def _adjust_color_temperature(self, img, temp_shift):
        """Adjust color temperature of an image"""
        try:
            img_array = np.array(img, dtype=np.float32)
            
            if temp_shift > 0:
                img_array[:, :, 2] *= (1 + temp_shift / 10000)
                img_array[:, :, 0] *= (1 - temp_shift / 20000)
            else: 
                img_array[:, :, 0] *= (1 - temp_shift / 10000)
                img_array[:, :, 2] *= (1 + temp_shift / 20000)
            
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
            return Image.fromarray(img_array, mode=img.mode)
        except Exception as e:
            logger.error(f"Error adjusting color temperature: {e}")
            return img
    
    def _analyze_positioning(self, character_desc, background_desc):
        """
        Analyze character and background descriptions to determine optimal positioning
        Returns positioning and sizing information
        """
        position_info = {
            'char_position': 'center',
            'char_size_factor': 0.6,
            'char_vertical_pos': 0.7,
            'depth_layer': 'foreground',
            'interaction_type': 'standing'
        }
        
        try:
            # Analyze character description for positioning clues
            char_lower = character_desc.lower()
            bg_lower = background_desc.lower()
            
            # Determine horizontal position
            if any(word in char_lower for word in ['left', 'side', 'corner']):
                position_info['char_position'] = 'left'
            elif any(word in char_lower for word in ['right', 'side', 'corner']):
                position_info['char_position'] = 'right'
            
            # Determine size based on environment scale
            if any(word in bg_lower for word in ['vast', 'enormous', 'massive', 'grand', 'towering']):
                position_info['char_size_factor'] = 0.4
            elif any(word in bg_lower for word in ['intimate', 'small', 'cozy', 'narrow']):
                position_info['char_size_factor'] = 0.8
            
            # Determine vertical position
            if any(word in char_lower for word in ['flying', 'floating', 'hovering']):
                position_info['char_vertical_pos'] = 0.3
            elif any(word in char_lower for word in ['sitting', 'crouching', 'kneeling']):
                position_info['char_vertical_pos'] = 0.9
            
            # Determine interaction type
            if any(word in char_lower for word in ['running', 'jumping', 'fighting', 'dancing']):
                position_info['interaction_type'] = 'action'
            elif any(word in char_lower for word in ['sitting', 'resting', 'reading']):
                position_info['interaction_type'] = 'sitting'
            
        except Exception as e:
            logger.error(f"Error analyzing positioning: {e}")
        
        return position_info
    
    def _prepare_character_for_composition(self, char_img, position_info):
        """
        Prepare character image for composition (background removal, resizing, etc.)
        Uses OpenCV for advanced processing
        """
        try:
            # Resize character based on position info
            target_size = int(min(char_img.size) * position_info['char_size_factor'])
            aspect_ratio = char_img.size[0] / char_img.size[1]

            if aspect_ratio > 1:
                new_size = (target_size, int(target_size / aspect_ratio))
            else:
                new_size = (int(target_size * aspect_ratio), target_size)

            # First resize based on position info
            char_img_resized = char_img.resize(new_size, Image.Resampling.LANCZOS)

            # Additional shrink to 55%
            scale_factor = 0.55
            final_size = (int(char_img_resized.size[0] * scale_factor),
                        int(char_img_resized.size[1] * scale_factor))
            char_img_resized = char_img_resized.resize(final_size, Image.Resampling.LANCZOS)

            # Apply subtle background removal/softening
            char_cv = cv2.cvtColor(np.array(char_img_resized.convert('RGB')), cv2.COLOR_RGB2BGR)
            
            # Create a soft mask to isolate the character (simple approach)
            gray = cv2.cvtColor(char_cv, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
            
            # Apply morphological operations to refine mask
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Apply Gaussian blur to soften edges
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            
            # Convert back to PIL with alpha channel
            mask_pil = Image.fromarray(mask).convert('L')
            char_img_resized.putalpha(mask_pil)
            
            return char_img_resized
            
        except Exception as e:
            logger.error(f"Error preparing character: {e}")
            return char_img.resize((300, 400))
    
    def _prepare_background_for_composition(self, bg_img, position_info):
        """
        Prepare background image for character placement
        """
        try:
            # Standard background size
            target_size = (800, 600)
            bg_prepared = bg_img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Apply subtle depth-of-field effect if character is in foreground
            if position_info['depth_layer'] == 'foreground':
                bg_cv = cv2.cvtColor(np.array(bg_prepared), cv2.COLOR_RGB2BGR)
                bg_cv = cv2.GaussianBlur(bg_cv, (3, 3), 0)
                bg_prepared = Image.fromarray(cv2.cvtColor(bg_cv, cv2.COLOR_BGR2RGB))
            
            return bg_prepared
            
        except Exception as e:
            logger.error(f"Error preparing background: {e}")
            return bg_img.resize((800, 600))
    
    def _composite_final_scene(self, char_img, bg_img, position_info):
        """
        Composite character onto background using proper positioning and blending
        """
        try:
            # Background removal
            try:
                char_img = remove(char_img)
            except Exception as e:
                logger.warning(f"Background removal failed: {e}")

            # Create the final composition
            final_img = bg_img.copy().convert('RGBA')
            
            # Calculate character position
            bg_width, bg_height = bg_img.size
            char_width, char_height = char_img.size
            
            # Horizontal positioning
            if position_info['char_position'] == 'left':
                x_offset = bg_width // 9
            elif position_info['char_position'] == 'right':
                x_offset = bg_width - char_width - (bg_width // 9)
            else:  # center
                x_offset = (bg_width - char_width) // 2
            
            # Vertical positioning
            y_offset = int(bg_height * position_info['char_vertical_pos'] - char_height)
            y_offset = max(0, min(y_offset, bg_height - char_height))
            
            # Composite character onto background
            if char_img.mode == 'RGBA':
                final_img.paste(char_img, (x_offset, y_offset), char_img)
            else:
                final_img.paste(char_img, (x_offset, y_offset))
            
            return final_img.convert('RGB')
            
        except Exception as e:
            logger.error(f"Error compositing final scene: {e}")
            total_width = bg_img.size[0] + char_img.size[0]
            max_height = max(bg_img.size[1], char_img.size[1])
            
            combined = Image.new('RGB', (total_width, max_height), (255, 255, 255))
            combined.paste(bg_img, (0, 0))
            combined.paste(char_img, (bg_img.size[0], 0))
            return combined
    
    def _apply_scene_post_processing(self, combined_img, genre):
        """
        Apply final post-processing effects based on genre
        """
        try:
            # Apply genre-specific effects
            if genre in ['horror', 'mystery']:
                # Darken and increase contrast
                enhancer = ImageEnhance.Brightness(combined_img)
                combined_img = enhancer.enhance(0.8)
                enhancer = ImageEnhance.Contrast(combined_img)
                combined_img = enhancer.enhance(1.2)
                
            elif genre in ['fantasy', 'adventure']:
                # Enhance colors and saturation
                enhancer = ImageEnhance.Color(combined_img)
                combined_img = enhancer.enhance(1.1)
                
            elif genre in ['romance', 'drama']:
                # Soften and warm the image
                enhancer = ImageEnhance.Contrast(combined_img)
                combined_img = enhancer.enhance(0.9)
                
            elif genre == 'sci-fi':
                # Cool the colors slightly
                img_array = np.array(combined_img, dtype=np.float32)
                img_array[:, :, 2] *= 1.05
                img_array[:, :, 0] *= 0.98
                combined_img = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
            
            # Apply subtle sharpening
            combined_img = combined_img.filter(ImageFilter.UnsharpMask(radius=1, percent=50, threshold=2))
            
            return combined_img
            
        except Exception as e:
            logger.error(f"Error in post-processing: {e}")
            return combined_img
    
    def generate_complete_story(self, prompt, length='medium', genre='fantasy'):
        """Generate story, character description, and background description in a single chain """
        
        length_instructions = {
            'short': 'Write a complete short story of 200-300 words with clear beginning, middle, and end.',
            'medium': 'Write a complete medium-length story of 300-500 words with developed plot and character arc.',
            'long': 'Write a complete longer story of 500-750 words with rich detail and compelling narrative.'
        }
        
        unified_template = PromptTemplate(
            input_variables=["prompt", "genre", "length_instruction"],
            template="""
            You are a professional storyteller and world-builder. Create a complete story package with three DISTINCT sections:

            STORY REQUIREMENTS:
            {length_instruction}
            Genre: {genre}
            User Prompt: {prompt}

            SECTION 1: **[STORY]**
            Write a complete, engaging story based on the prompt above. Focus ONLY on the narrative:
            - Clear beginning, middle, and end
            - Vivid storytelling with natural dialogue
            - Immersive scenes and plot development
            - DO NOT include character descriptions or world-building details here
            - Focus purely on the story events and narrative flow

            SECTION 2: **[CHARACTER]**
            Create a detailed character profile for the main protagonist (150-200 words):
            - PHYSICAL: Age, height, build, hair color/style, eye color, facial features, clothing style
            - PERSONALITY: Core traits, strengths, flaws, mannerisms, speaking style
            - BACKGROUND: Family history, education, past experiences, formative events
            - MOTIVATION: Primary goals, fears, desires, what drives them
            - SKILLS: Talents, abilities, expertise, weaknesses
            - Keep this SEPARATE from the story - focus only on character details

            SECTION 3: **[BACKGROUND]**
            Develop the world and setting (180-220 words):
            - PHYSICAL SETTING: Geography, climate, architecture, landscapes
            - TIME/ERA: Historical period, technology level, cultural context
            - SOCIETY: Social structure, customs, languages, beliefs, politics
            - ATMOSPHERE: Mood, tone, environmental details, ambiance
            - UNIQUE ELEMENTS: Special features, magic systems, technologies, mysteries
            - Keep this SEPARATE from both story and character - focus only on world details

            FORMATTING RULES:
            - Use EXACTLY these headers: **[STORY]**, **[CHARACTER]**, **[BACKGROUND]**
            - Keep each section completely distinct and focused
            - Ensure all sections are consistent within the same fictional universe
            - Write in a {genre} style throughout all sections
            """
        )
        
        if not self.llm:
            return self._generate_mock_complete_story(prompt, genre)
        
        try:
            chain = unified_template | self.llm | StrOutputParser()
            complete_response = chain.invoke({
                "prompt": prompt,
                "genre": genre,
                "length_instruction": length_instructions[length]
            })
            
            return self._parse_response(complete_response)
            
        except Exception as e:
            logger.error(f"Error generating complete story: {e}")
            return self._generate_mock_complete_story(prompt, genre)
    
    def generate_character_image_prompt(self, character_description, visual_style, genre):
        """Generate an optimized character image prompt - IMPROVED VERSION"""
        
        prompt_template = PromptTemplate(
            input_variables=["character_description", "visual_style", "genre"],
            template="""
            Extract ONLY the visual/physical details from this character description:
            {character_description}

            Create a focused image prompt for a {genre} character portrait with these requirements:
            
            EXTRACT ONLY:
            - Age and physical build
            - Hair color, style, and length
            - Eye color and facial features
            - Clothing and accessories
            - Any distinctive physical marks or features
            
            IGNORE:
            - Personality traits
            - Background history
            - Skills and abilities
            - Motivations and goals
            - Story context
            
            FORMAT: Create a single comma-separated prompt under 150 characters:
            "portrait of [age] [build] [gender], [hair details], [eye color], [clothing style], {visual_style}, high quality, detailed"
            
            Visual Image Prompt:
            """
        )
        
        if not self.llm:
            return self._generate_mock_image_prompt(character_description, genre)
        
        try:
            chain = prompt_template | self.llm | StrOutputParser()
            image_prompt = chain.invoke({
                "character_description": character_description,
                "visual_style": visual_style,
                "genre": genre
            })
            
            cleaned_prompt = self._clean_image_prompt(image_prompt.strip())
            return f"{cleaned_prompt}, {visual_style}"
            
        except Exception as e:
            logger.error(f"Error generating character image prompt: {e}")
            return self._generate_mock_image_prompt(character_description, genre)
    
    def generate_background_image_prompt(self, background_description, story_context, visual_style, genre):
        """Generate an optimized background/environment image prompt - IMPROVED VERSION"""
        
        background_prompt_template = PromptTemplate(
            input_variables=["background_description", "visual_style", "genre"],
            template="""
            Extract ONLY the visual/environmental details from this background description:
            {background_description}

            Create a focused environment image prompt for a {genre} setting with these requirements:
            
            EXTRACT ONLY:
            - Geographic features (mountains, forests, cities, etc.)
            - Architecture and structures
            - Climate and weather
            - Time of day/lighting
            - Physical atmosphere and mood
            - Landscape elements
            
            IGNORE:
            - Characters or people
            - Story events
            - Social/political details
            - Historical context
            - Cultural information
            
            FORMAT: Create a single comma-separated prompt under 150 characters:
            "[environment type], [architectural style], [lighting/time], [weather/atmosphere], {visual_style}, no people, landscape"
            
            Environment Image Prompt:
            """
        )
        
        if not self.llm:
            return self._generate_mock_background_image_prompt(background_description, genre)
        
        try:
            chain = background_prompt_template | self.llm | StrOutputParser()
            image_prompt = chain.invoke({
                "background_description": background_description,
                "visual_style": visual_style,
                "genre": genre
            })
            
            cleaned_prompt = self._clean_background_image_prompt(image_prompt.strip())
            return f"{cleaned_prompt}, {visual_style}, no people, wide shot"
            
        except Exception as e:
            logger.error(f"Error generating background image prompt: {e}")
            return self._generate_mock_background_image_prompt(background_description, genre)
    
    def generate_character_image(self, character_description, visual_style, genre):
        """Generate character image using free Hugging Face models"""
        
        try:
            # First, generate optimized image prompt
            image_prompt = self.generate_character_image_prompt(character_description, visual_style, genre)
            
            # Add consistent character-specific enhancers
            full_prompt = (
                f"{image_prompt}, portrait, character design, centered composition, "
                f"detailed face, professional lighting, high quality, masterpiece, "
                f"transparent background, isolated subject, PLAIN WHITE background, no scenery"
                f"Give the character with PLAIN WHITE BACKGROUND, and give the full body shot, head to toe, character standing."
                )

            # Try multiple models until one works
            for model in self.hf_image_models:
                try:
                    image_data = self._call_huggingface_api(model, full_prompt, image_type="portrait")
                    if image_data:
                        return {
                            'image_data': image_data,
                            'prompt': full_prompt,
                            'model_used': model,
                            'success': True,
                            'type': 'character'
                        }
                except Exception as e:
                    logger.warning(f"Failed to generate character with {model}: {e}")
                    continue
            
            # If all models fail, return placeholder
            return self._generate_placeholder_image("character")
            
        except Exception as e:
            logger.error(f"Error in character image generation: {e}")
            return self._generate_placeholder_image("character")

    def generate_background_image(self, background_description, story_context, visual_style, genre):
        """Generate background/environment image using free Hugging Face models"""
        
        try:
            # First, generate optimized background image prompt
            image_prompt = self.generate_background_image_prompt(background_description, story_context, visual_style, genre)
            
            # Add consistent environment-specific enhancers
            full_prompt = f"{image_prompt}, wide shot, landscape photography, environmental art, cinematic lighting, no people, high quality, detailed, masterpiece"
            
            # Try multiple models until one works
            for model in self.hf_image_models:
                try:
                    image_data = self._call_huggingface_api(model, full_prompt, image_type="landscape")
                    if image_data:
                        return {
                            'image_data': image_data,
                            'prompt': full_prompt,
                            'model_used': model,
                            'success': True,
                            'type': 'background'
                        }
                except Exception as e:
                    logger.warning(f"Failed to generate background with {model}: {e}")
                    continue
            
            # If all models fail, return placeholder
            return self._generate_placeholder_image("background")
            
        except Exception as e:
            logger.error(f"Error in background image generation: {e}")
            return self._generate_placeholder_image("background")
    
    def _get_visual_style_for_genre(self, genre):
        """Return consistent visual style parameters for each genre"""
        style_mapping = {
            'fantasy': 'fantasy art style, magical lighting, ethereal atmosphere',
            'sci-fi': 'science fiction art style, futuristic, cyberpunk lighting',
            'mystery': 'noir style, dramatic shadows, moody atmosphere',
            'romance': 'romantic art style, soft lighting, dreamy atmosphere',
            'adventure': 'adventure art style, dynamic lighting, epic atmosphere',
            'horror': 'gothic horror style, dark atmosphere, ominous lighting',
            'drama': 'realistic art style, natural lighting, contemporary',
            'comedy': 'bright art style, cheerful lighting, colorful atmosphere'
        }
        return style_mapping.get(genre, 'realistic art style, natural lighting')
    
    def _call_stability_api(self, prompt, image_type="portrait"):
        """Call Stability.ai API as fallback when HF models fail."""
        try:
            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "width": 1024,
                "height": 1024,
                "samples": 1
            }
            url = self.stability_url_map[image_type]
            resp = requests.post(url, headers=self.stability_headers, json=payload, timeout=40)
            if resp.status_code != 200:
                logger.error(f"Stability API error {resp.status_code}: {resp.text}")
                return None

            data = resp.json()
            img_b64 = data["artifacts"][0]["base64"]
            return img_b64
        except Exception as e:
            logger.error(f"Error calling Stability API: {e}")
            return None

    def _call_huggingface_api(self, model, prompt, max_retries=3, image_type="portrait"):
        """Call Hugging Face Inference API, fallback to Stability.ai if fails."""
        
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        if image_type == "landscape":
            width, height = 768, 512
            guidance_scale = 7.0
        else:
            width, height = 512, 768
            guidance_scale = 8.0
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 25,
                "guidance_scale": guidance_scale,
                "width": width,
                "height": height,
                "negative_prompt": "blurry, low quality, distorted, watermark, text, multiple people" if image_type == "portrait" else "people, characters, figures, blurry, low quality, distorted, watermark, text"
            }
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(api_url, headers=self.hf_headers, json=payload, timeout=35)
                
                if response.status_code == 200:
                    image_bytes = response.content
                    image = Image.open(BytesIO(image_bytes))
                    
                    # Convert to base64 for storage/display
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    return img_base64
                
                elif response.status_code == 503:
                    logger.info(f"Model {model} is loading, waiting...")
                    time.sleep(15)
                    continue
                
                else:
                    logger.error(f"HF API call failed: {response.status_code} - {response.text}")
                    break
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(8)
                continue
            except Exception as e:
                logger.error(f"HF API call error: {e}")
                break
        
        # Stability.ai fallback
        logger.info("Falling back to Stability API...")
        return self._call_stability_api(prompt, image_type=image_type)
    
    def _clean_image_prompt(self, prompt):
        """Clean and optimize character image prompt"""
        unwanted_phrases = [
            "Visual Image Prompt:", "Image Prompt:", "Based on", "character description", 
            "This character", "The protagonist", "story", "personality", "motivation",
            "background", "skills", "Extract ONLY:", "FORMAT:", "portrait of", "CREATE"
        ]
        
        cleaned = prompt
        for phrase in unwanted_phrases:
            cleaned = re.sub(phrase, "", cleaned, flags=re.IGNORECASE)
        
        # Clean up spacing and punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip().strip(',').strip()
        
        # Remove quotes if present
        cleaned = cleaned.strip('"').strip("'")
        
        return cleaned
    
    def _clean_background_image_prompt(self, prompt):
        """Clean and optimize background image prompt"""
        unwanted_phrases = [
            "Environment Image Prompt:", "Image Prompt:", "Based on", "background description", 
            "story context", "This environment", "The setting", "characters", "people",
            "Extract ONLY:", "FORMAT:", "CREATE", "IGNORE:"
        ]
        
        cleaned = prompt
        for phrase in unwanted_phrases:
            cleaned = re.sub(phrase, "", cleaned, flags=re.IGNORECASE)
        
        # Clean up spacing and punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip().strip(',').strip()
        
        # Remove quotes if present
        cleaned = cleaned.strip('"').strip("'")
        
        # Add environment-specific terms if missing
        environment_terms = ["landscape", "environment", "scenery", "setting"]
        if not any(term in cleaned.lower() for term in environment_terms):
            cleaned = f"landscape, {cleaned}"
        
        return cleaned
    
    def _generate_mock_image_prompt(self, character_description, genre):
        """Generate fallback character image prompt"""
        # Extract basic features from description
        age_match = re.search(r'(\d+)\s*years?\s*old', character_description, re.IGNORECASE)
        age = age_match.group(1) if age_match else "young adult"
        
        hair_colors = ["auburn", "black", "brown", "blonde", "red", "dark", "light"]
        hair_color = next((color for color in hair_colors if color in character_description.lower()), "brown")
        
        style = self._get_visual_style_for_genre(genre)
        return f"portrait of {age} year old person, {hair_color} hair, detailed face, {style}"
    
    def _generate_mock_background_image_prompt(self, background_description, genre):
        """Generate fallback background image prompt"""
        # Extract basic environmental features
        locations = ["forest", "castle", "library", "mountain", "city", "village", "temple", "desert"]
        location = next((loc for loc in locations if loc in background_description.lower()), "mystical landscape")
        
        times = ["dawn", "dusk", "night", "day", "twilight"]
        time_of_day = next((time for time in times if time in background_description.lower()), "atmospheric lighting")
        
        style = self._get_visual_style_for_genre(genre)
        return f"{location} environment, {time_of_day}, {style}, no people"
    
    def _generate_placeholder_image(self, image_type):
        """Generate a placeholder when image generation fails"""
        return {
            'image_data': None,
            'prompt': f"{image_type.title()} image generation unavailable",
            'model_used': "placeholder",
            'success': False,
            'placeholder': True,
            'type': image_type
        }
    
    def _parse_response(self, response):
        """Parse the unified response into separate components - IMPROVED VERSION"""
        try:
            # Use more precise regex to find sections
            story_match = re.search(r'\*\*\[STORY\]\*\*(.*?)(?=\*\*\[CHARACTER\]\*\*|$)', response, re.DOTALL | re.IGNORECASE)
            character_match = re.search(r'\*\*\[CHARACTER\]\*\*(.*?)(?=\*\*\[BACKGROUND\]\*\*|$)', response, re.DOTALL | re.IGNORECASE)
            background_match = re.search(r'\*\*\[BACKGROUND\]\*\*(.*?)$', response, re.DOTALL | re.IGNORECASE)
            
            # Also try without asterisks
            if not story_match:
                story_match = re.search(r'\[STORY\](.*?)(?=\[CHARACTER\]|$)', response, re.DOTALL | re.IGNORECASE)
            if not character_match:
                character_match = re.search(r'\[CHARACTER\](.*?)(?=\[BACKGROUND\]|$)', response, re.DOTALL | re.IGNORECASE)
            if not background_match:
                background_match = re.search(r'\[BACKGROUND\](.*?)$', response, re.DOTALL | re.IGNORECASE)
            
            story = story_match.group(1).strip() if story_match else ""
            character = character_match.group(1).strip() if character_match else ""
            background = background_match.group(1).strip() if background_match else ""
            
            # Clean up the extracted content
            story = self._clean_section_content(story)
            character = self._clean_section_content(character)
            background = self._clean_section_content(background)
            
            # Fallback if sections not clearly marked
            if not all([story, character, background]):
                return self._fallback_parse(response)
            
            return {
                'story': story,
                'character_description': character,
                'background_description': background
            }
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return self._fallback_parse(response)
    
    def _clean_section_content(self, content):
        """Clean individual section content"""
        if not content:
            return ""
        
        # Remove section headers that might have leaked through
        content = re.sub(r'\*\*\[(STORY|CHARACTER|BACKGROUND)\]\*\*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\[(STORY|CHARACTER|BACKGROUND)\]', '', content, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = content.strip()
        
        return content
    
    def _fallback_parse(self, response):
        """Fallback parsing if section headers aren't found - IMPROVED VERSION"""
        # Try to split by common paragraph patterns
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        
        if len(paragraphs) >= 6:
            # Assume first 1/3 is story, middle 1/3 is character, last 1/3 is background
            story_end = len(paragraphs) // 2
            character_end = 2 * len(paragraphs) // 6
            
            return {
                'story': '\n\n'.join(paragraphs[:story_end]).strip(),
                'character_description': '\n\n'.join(paragraphs[story_end:character_end]).strip(),
                'background_description': '\n\n'.join(paragraphs[character_end:]).strip()
            }
        else:
            # If parsing fails completely, return mock data with partial response
            mock_data = self._generate_mock_complete_story("fallback prompt", "fantasy")
            if len(response) > 100:
                mock_data['story'] = response[:500] + "..." if len(response) > 500 else response
            return mock_data
    
    def _generate_mock_complete_story(self, prompt, genre):
        """Fallback complete story generator - keeping the existing implementation"""
        return {
            'story': f"""
Sarah discovered the mysterious oak tree in her backyard, shimmering with otherworldly 
energy and etched with unknown symbols. When she touched its bark, the world shifted.

She found herself in a vast magical library filled with floating books and glowing orbs. 
An elderly woman with silver hair emerged from the towering bookshelves.

"Welcome, Sarah. We've been waiting for you," the woman said. "You have the gift - 
the ability to step between worlds and read the stories between reality's lines. 
This library contains every story imagined and yet to be told."

Books of every size floated gracefully, some open with self-turning pages, others 
glowing with inner light. "Choose a story," the woman gestured. "Step inside it, 
live it, and help it reach its proper ending. Some stories have lost their way."

Sarah reached for a golden-glowing leather book. As she opened it, the world dissolved, 
and she fell into a new adventure.

Hours later, she returned home to find the oak tree gone, but carried the knowledge 
that magic existed everywhere, waiting for those brave enough to seek it.
            """.strip(),
            
            'character_description': """
PHYSICAL APPEARANCE:
Sarah Mitchell, 28, athletic 5'6" build with auburn hair in natural waves to her shoulders. 
Bright emerald eyes sparkle with curiosity, complemented by a small scar above her left eyebrow 
from childhood adventures. Favors practical clothing - worn jeans, comfortable boots, and a 
weathered leather jacket that belonged to her grandmother.

PERSONALITY & BACKGROUND:
Possesses insatiable curiosity that often leads her into unexpected situations. Growing up 
with her grandmother, a former librarian and storyteller, she developed a deep love for books 
and mystery. Her natural bravery sometimes borders on recklessness, but quick thinking and 
resourcefulness usually see her through challenges. Works as a research librarian but dreams 
of grand adventures beyond her quiet life.

MOTIVATIONS & SKILLS:
Driven by desire to discover hidden truths and experience the magic she's read about in 
countless books. Excellent research skills, keen observational abilities, and surprising 
problem-solving talents. Greatest fear is living an ordinary, unremarkable life; deepest 
desire is finding real magic in the world.
            """.strip(),
            
            'background_description': """
PHYSICAL ENVIRONMENT:
The story unfolds where modern suburban reality intersects with ancient magical realms. 
Ordinary neighborhoods with tree-lined streets and colonial homes exist alongside mystical 
pocket dimensions accessible through natural portals. The magical library realm features 
impossibly vast spaces with soaring crystal spires, floating islands of books connected 
by bridges of pure light, and architecture that defies conventional physics.

SOCIETY & CULTURE:
This world operates on two levels - the mundane human society where most people live unaware 
of magic, and the hidden magical community governed by the ancient Order of Keepers. The 
Keepers maintain the balance between worlds, preserving stories and knowledge across dimensions. 
Magic users are rare, often discovering their abilities through chance encounters with mystical 
artifacts or locations.

TIME & SYSTEMS:
Set in contemporary times, this world blends modern technology with ancient magical systems. 
The library realm exists outside normal time, where minutes can pass as hours in the real world. 
Magic is powered by imagination, belief, and the collective unconscious of all storytelling humanity.

UNIQUE ELEMENTS:
Stories themselves are living entities capable of growing, changing, and influencing reality. 
The library serves as a nexus where every tale ever imagined takes physical form, and gifted 
individuals can literally step into narratives to guide their outcomes and help lost stories 
find their proper endings.
            """.strip()
        }