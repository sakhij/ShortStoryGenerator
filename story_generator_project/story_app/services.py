from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import logging
import re
import requests
import base64
from io import BytesIO
from PIL import Image
import time
import os

logger = logging.getLogger(__name__)
load_dotenv()

class StoryGeneratorService:
    def __init__(self):
        try:
            self.llm = OllamaLLM(model="gemma:2b")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            self.llm = None
        
        # Hugging Face Inference API endpoints (free tier)
        self.hf_image_models = [
            "black-forest-labs/FLUX.1-schnell",  # Fast and free
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5",
            "CompVis/stable-diffusion-v1-4"
        ]
        
        # Get HF token from environment variable for security
        hf_token = os.getenv('HUGGINGFACE_TOKEN', 'abc')
        self.hf_headers = {
            "Authorization": f"Bearer {hf_token}"
        }
    
    def generate_complete_story_with_images(self, prompt, length='medium', genre='fantasy'):
        """Generate story, character description, background description, character image, and background image"""
        
        # First generate the complete story package
        story_package = self.generate_complete_story(prompt, length, genre)
        
        # Extract visual style consistency parameters from genre
        visual_style = self._get_visual_style_for_genre(genre)
        
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
        
        return story_package
    
    def generate_complete_story(self, prompt, length='medium', genre='fantasy'):
        """Generate story, character description, and background description in a single chain - IMPROVED VERSION"""
        
        length_instructions = {
            'short': 'Write a complete short story of 200-300 words with clear beginning, middle, and end.',
            'medium': 'Write a complete medium-length story of 300-500 words with developed plot and character arc.',
            'long': 'Write a complete longer story of 500-750 words with rich detail and compelling narrative.'
        }
        
        # IMPROVED: More structured and separated template
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
            
            # Parse the response to extract individual sections
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
            
            # Clean and optimize the prompt
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
            
            # Clean and optimize the prompt
            cleaned_prompt = self._clean_background_image_prompt(image_prompt.strip())
            return f"{cleaned_prompt}, {visual_style}, no people, wide shot"
            
        except Exception as e:
            logger.error(f"Error generating background image prompt: {e}")
            return self._generate_mock_background_image_prompt(background_description, genre)
    
    def generate_character_image(self, character_description, visual_style, genre):
        """Generate character image using free Hugging Face models - IMPROVED VERSION"""
        
        try:
            # First, generate optimized image prompt
            image_prompt = self.generate_character_image_prompt(character_description, visual_style, genre)
            
            # Add consistent character-specific enhancers
            full_prompt = f"{image_prompt}, portrait, character design, centered composition, detailed face, professional lighting, high quality, masterpiece"
            
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
        """Generate background/environment image using free Hugging Face models - IMPROVED VERSION"""
        
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
    
    def _call_huggingface_api(self, model, prompt, max_retries=3, image_type="portrait"):
        """Call Hugging Face Inference API with optimized parameters for different image types"""
        
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        # Optimize parameters based on image type - IMPROVED CONSISTENCY
        if image_type == "landscape":
            width, height = 768, 512  # Wider for landscapes
            guidance_scale = 7.0  # Slightly lower for environments
        else:  # portrait
            width, height = 512, 768  # Taller for characters
            guidance_scale = 8.0  # Higher for character details
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 25,  # Slightly higher for better quality
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
                    # Return base64 encoded image data
                    image_bytes = response.content
                    image = Image.open(BytesIO(image_bytes))
                    
                    # Convert to base64 for storage/display
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    return img_base64
                
                elif response.status_code == 503:  # Model loading
                    logger.info(f"Model {model} is loading, waiting...")
                    time.sleep(15)
                    continue
                    
                else:
                    logger.error(f"API call failed: {response.status_code} - {response.text}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(8)
                continue
            except Exception as e:
                logger.error(f"API call error: {e}")
                return None
        
        return None
    
    def _clean_image_prompt(self, prompt):
        """Clean and optimize character image prompt - IMPROVED VERSION"""
        # Remove unwanted phrases more thoroughly
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
        """Clean and optimize background image prompt - IMPROVED VERSION"""
        # Remove unwanted phrases more thoroughly
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
            story_end = len(paragraphs) // 3
            character_end = 2 * len(paragraphs) // 3
            
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