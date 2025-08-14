# Prompt Engineering Documentation
## AI Story Generator - Complete Guide

### Table of Contents
1. [Overview](#overview)
2. [Story Generation Prompts](#story-generation-prompts)
3. [Character Image Prompts](#character-image-prompts)
4. [Background Image Prompts](#background-image-prompts)
5. [Scene Composition](#scene-composition)
6. [Audio Processing](#audio-processing)
7. [Prompt Optimization Strategies](#prompt-optimization-strategies)
8. [Example Workflows](#example-workflows)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The AI Story Generator uses a sophisticated multi-stage prompt engineering approach to create complete story packages. Each component (story, character, background, images) uses specialized prompts designed for optimal AI model performance.

### Core Principles
- **Separation of Concerns**: Each prompt handles one specific task
- **Context Preservation**: Information flows between stages consistently
- **Error Resilience**: Fallback mechanisms for failed generations
- **Genre Consistency**: Style maintained across all components

### Processing Pipeline
```
User Input → Story Prompt → Character Prompt → Background Prompt → Image Prompts → Composition
```

---

## Story Generation Prompts

### Unified Story Template

The main story generation uses a structured template that produces three distinct sections in a single LLM call:

```python
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
```

### Length Instructions

Different length parameters provide specific guidance:

```python
length_instructions = {
    'short': 'Write a complete short story of 200-300 words with clear beginning, middle, and end.',
    'medium': 'Write a complete medium-length story of 300-500 words with developed plot and character arc.',
    'long': 'Write a complete longer story of 500-750 words with rich detail and compelling narrative.'
}
```

### Genre-Specific Adaptations

The template automatically adapts based on genre:

- **Fantasy**: Magical elements, mythical creatures, world-building focus
- **Sci-Fi**: Technology, futuristic settings, scientific concepts
- **Mystery**: Suspense, clues, investigation elements
- **Romance**: Emotional connections, relationship development
- **Horror**: Atmospheric tension, supernatural elements
- **Adventure**: Action sequences, exploration, challenges

### Example Story Output

**Input**: "A librarian discovers a magical book"
**Genre**: Fantasy
**Length**: Medium

```
**[STORY]**
The weathered oak doors creaked open with a rusty groan, revealing a dusty, cobweb-laden chamber. Sarah, the librarian, stumbled into the darkness, a shiver running down her spine. Her heart hammered against her ribs like a frantic bird trapped in a cage.

She clutched the ancient book in her trembling hand, its leather cover cracked and worn. It was inscribed with swirling symbols she had never seen before. She had stumbled upon a legend whispered amongst the old books of the library - a magical book, a portal to another world.

Her fingers trembled as she flipped open the book, a cold wind rushing through her hair. The air was thick with the scent of forgotten pages and the faintest hint of magic. She knew she had to protect this precious relic, its secrets too precious to be shared.

Days bled into nights, the book her only solace. She would spend hours poring over its pages, deciphering the cryptic symbols and cryptic scripts. Her determination grew with each passing day.

One stormy night, a strange energy surged through the book, illuminating Sarah's face. She gasped, a surge of excitement coursing through her body. The book was alive! Its pages whispered secrets, revealing stories of a forgotten land, a world bathed in the soft light of a thousand candles.

She knew this was her calling, her destiny. She had to share this knowledge with the world, to warn people of the hidden realm beyond the veil. But fear gnawed at her, a constant reminder of her solitude and the danger she faced.

**[CHARACTER]**
**Name:** Anya, a young woman with fiery hair that tumbled down her shoulders and eyes that mirrored the sky.

**Appearance:** Anya was a stunning mix of fiery and serene. Her porcelain skin held a hint of pale blue, her eyes shone with an intelligence that seemed to burn with an endless potential. Her slender frame was built for adventure, her long limbs and sharp features adapted for the life she led.

**Background:** Anya grew up in a bustling city, surrounded by the bustle of life. Her childhood was filled with books and stories, her imagination her only escape from the concrete jungle. Her parents, both scholars, nurtured her thirst for knowledge, exposing her to the wonders of history, science, and the arts.

**Motivation:** Anya's primary motivation was the desire to protect the world from a looming darkness. She believed that the magic of the book could offer a beacon of hope and inspire a new generation to fight for a better future.

**Skills:** Anya possessed an uncanny ability to learn languages, her vast knowledge spanning multiple cultures and eras. She was also a gifted scholar, her thirst for knowledge insatiable.

**Background:**

* **Geography:** Anya grew up in a bustling city with towering skyscrapers and a vibrant social life.
* **Time/Era:** Anya lived in the Renaissance, a time marked by scientific advancements and cultural enlightenment.
* **Society:** The society was stratified, with a ruling class that controlled power and the lower classes struggling for survival.
* **Language:** Anya spoke multiple languages fluently, including Latin, Greek, French, and Arabic.
* **Culture:** Anya's culture was characterized by intellectual pursuits, artistic expression, and a strong sense of community.
* **Magic System:** Anya discovered she was a conduit for a rare and powerful magic known as "Celestial Aura."

**[BACKGROUND]**
Anya's world was a tapestry woven from ancient secrets and modern marvels. The city she called home was a vibrant melting pot of cultures, a place where history and modernity intertwined seamlessly. But beyond the city's gleaming facades lay a hidden world veiled in mystery.

The library, her sanctuary, held untold stories and ancient artifacts. She spent countless hours studying the book, uncovering its magical secrets and the stories it whispered. With each turn of the pages, she felt a deeper connection to the world, to the lives she could touch with her magic.

The discovery of the book ignited a spark of determination within her. She knew her destiny lay in sharing the story of the Celestial Aura with the world. She envisioned a world where people, from all walks of life, could find a sense of wonder and hope in the ancient magic hidden beyond the veil.
```

---

## Character Image Prompts

### Character Image Template

```python
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
```

### Character Prompt Enhancement

The system adds specific enhancements for character generation:

```python
full_prompt = (
    f"{image_prompt}, portrait, character design, centered composition, "
    f"detailed face, professional lighting, high quality, masterpiece, "
    f"PLAIN WHITE background, no scenery, full body shot, head to toe, character standing"
)
```

### Visual Style Mapping

Genre-specific visual styles are applied:

```python
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
```

### Example Character Prompts

**Input Character Description**:
```
Anya, a young woman with fiery hair that tumbled down her shoulders and eyes that mirrored the sky. Anya was a stunning mix of fiery and serene. Her porcelain skin held a hint of pale blue, her eyes shone with an intelligence that seemed to burn with an endless potential. Her slender frame was built for adventure, her long limbs and sharp features adapted for the life she led.
```

**Generated Character Prompt**:
```
25, slender, female, fiery hair that tumbles down her shoulders, sky-blue eyes, flowing gown adorned with intricate patterns, a hint of pale blue in her porcelain skin, magical aura emanating from her body, fantasy art style, magical lighting, ethereal atmosphere, portrait, character design, centered composition, detailed face, professional lighting, high quality, masterpiece, transparent background, isolated subject, PLAIN WHITE background, no sceneryGive the character with PLAIN WHITE BACKGROUND, and give the full body shot, head to toe, character standing.
```

---

## Background Image Prompts

### Background Image Template

```python
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
```

### Background Enhancement

Additional elements are added to background prompts:

```python
full_prompt = f"{image_prompt}, wide shot, landscape photography, environmental art, cinematic lighting, no people, high quality, detailed, masterpiece"
```

### Example Background Prompts

**Input Background Description**:
```
Anya's world was a tapestry woven from ancient secrets and modern marvels. The city she called home was a vibrant melting pot of cultures, a place where history and modernity intertwined seamlessly. But beyond the city's gleaming facades lay a hidden world veiled in mystery.
```

**Generated Background Prompt**:
```
**"Ancient library sanctuary, mixed historical-modern architecture, soft interior lighting, mysterious veiled atmosphere, fantasy art style, magical lighting, ethereal atmosphere, no , landscape**, fantasy art style, magical lighting, ethereal atmosphere, no people, wide shot, wide shot, landscape photography, environmental art, cinematic lighting, no people, high quality, detailed, masterpiece
```

---

## Scene Composition

### Image Combination Process

The system combines character and background images using a sophisticated pipeline:

1. **Style Matching**: Adjusts lighting and color temperature
2. **Position Analysis**: Determines optimal character placement
3. **Background Removal**: Uses rembg library for character isolation
4. **Composition**: Places character in scene with proper scaling
5. **Post-Processing**: Applies genre-specific effects

### Position Analysis Logic

```python
def _analyze_positioning(self, character_desc, background_desc):
    position_info = {
        'char_position': 'center',  # center, left, right
        'char_size_factor': 0.6,    # Size relative to background
        'char_vertical_pos': 0.7,   # 0.0 = top, 1.0 = bottom
        'depth_layer': 'foreground', # foreground, midground, background
        'interaction_type': 'standing' # standing, sitting, action, etc.
    }
    
    # Analyze descriptions for positioning clues
    char_lower = character_desc.lower()
    bg_lower = background_desc.lower()
    
    # Determine horizontal position
    if any(word in char_lower for word in ['left', 'side', 'corner']):
        position_info['char_position'] = 'left'
    elif any(word in char_lower for word in ['right', 'side', 'corner']):
        position_info['char_position'] = 'right'
    
    return position_info
```

### Style Matching Algorithm

```python
def _match_image_styles(self, char_img, bg_img, genre):
    char_temp = self._calculate_color_temperature(char_array)
    bg_temp = self._calculate_color_temperature(bg_array)
    
    # Adjust character to match background style
    if abs(char_temp - bg_temp) > 500:
        char_img = self._adjust_color_temperature(char_img, bg_temp - char_temp)
    
    # Match brightness and contrast levels
    char_brightness = np.mean(char_array)
    bg_brightness = np.mean(bg_array)
    
    if abs(char_brightness - bg_brightness) > 20:
        brightness_factor = bg_brightness / char_brightness if char_brightness > 0 else 1.0
        brightness_factor = max(0.5, min(2.0, brightness_factor))
        enhancer = ImageEnhance.Brightness(char_img)
        char_img = enhancer.enhance(brightness_factor)
    
    return char_img, bg_img
```

---

## Audio Processing

### Whisper Integration

Audio transcription uses OpenAI Whisper with specific configurations:

```python
def transcribe_audio(self, audio_file):
    try:
        # Convert to compatible format using pydub
        audio = AudioSegment.from_file(temp_file_path)
        duration = len(audio) / 1000.0
        
        # Transcribe using Whisper
        result = self.whisper_model.transcribe(temp_file_path)
        transcription = result["text"].strip()
        
        return {
            'transcription': transcription,
            'duration': duration,
            'success': True,
            'language': result.get('language', 'unknown'),
            'segments': len(result.get('segments', []))
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### Audio Validation

```python
def validate_audio_file(self, audio_file):
    allowed_formats = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac']
    max_size = 10 * 1024 * 1024  # 10MB
    max_duration = 300  # 5 minutes
    
    # Validation checks
    if audio_file.size > max_size:
        return {'valid': False, 'error': 'File too large'}
    
    file_ext = os.path.splitext(audio_file.name.lower())[1]
    if file_ext not in allowed_formats:
        return {'valid': False, 'error': 'Unsupported format'}
```

### Mixed Input Processing

For combined text and audio inputs:

```python
def generate_story_from_mixed_input(self, text_prompt=None, audio_file=None, length='medium', genre='fantasy'):
    combined_prompt_parts = []
    
    # Add text prompt if provided
    if text_prompt and text_prompt.strip():
        combined_prompt_parts.append(f"Text prompt: {text_prompt}")
    
    # Add audio transcription if provided
    if audio_file:
        transcription_result = self.transcribe_audio(audio_file)
        if transcription_result['success']:
            combined_prompt_parts.append(f"Audio description: {transcription_result['transcription']}")
    
    # Combine all inputs into a single prompt
    combined_prompt = " | ".join(combined_prompt_parts)
```

---

## Prompt Optimization Strategies

### 1. Clear Section Separation

The system uses explicit section headers to ensure LLM output is properly structured:

```
**[STORY]** - Narrative content only
**[CHARACTER]** - Physical and personality details
**[BACKGROUND]** - World and setting information
```

### 2. Negative Instructions

Important "DO NOT" instructions prevent content bleeding between sections:

- "DO NOT include character descriptions in the story section"
- "Keep sections completely distinct and focused"
- "Focus purely on story events and narrative flow"

### 3. Length Constraints

Specific word count guidance ensures appropriate content length:

- Character descriptions: 150-200 words
- Background descriptions: 180-220 words
- Stories: Variable based on length parameter

### 4. Format Enforcement

Strict formatting rules ensure consistent parsing:

```python
# Parsing uses regex to extract sections
story_match = re.search(r'\*\*\[STORY\]\*\*(.*?)(?=\*\*\[CHARACTER\]\*\*|$)', response, re.DOTALL)
character_match = re.search(r'\*\*\[CHARACTER\]\*\*(.*?)(?=\*\*\[BACKGROUND\]\*\*|$)', response, re.DOTALL)
background_match = re.search(r'\*\*\[BACKGROUND\]\*\*(.*?)$', response, re.DOTALL)
```

### 5. Fallback Mechanisms

Multiple parsing strategies handle edge cases:

```python
def _fallback_parse(self, response):
    # Try splitting by paragraph patterns if headers fail
    paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
    
    if len(paragraphs) >= 6:
        story_end = len(paragraphs) // 3
        character_end = 2 * len(paragraphs) // 3
        
        return {
            'story': '\n\n'.join(paragraphs[:story_end]),
            'character_description': '\n\n'.join(paragraphs[story_end:character_end]),
            'background_description': '\n\n'.join(paragraphs[character_end:])
        }
```

### 6. Context Preservation

Information flows consistently between stages:

- Character descriptions inform image prompts
- Background descriptions guide environment generation
- Genre influences all components consistently
- Visual style maintained across all images

---

## Example Workflows

### Text-Only Generation

**Input**: "A time traveler gets stuck in the Victorian era"
**Genre**: Sci-Fi
**Length**: Medium

**Step 1**: Story Generation Prompt
```
You are a professional storyteller and world-builder. Create a complete story package...
Genre: sci-fi
User Prompt: A time traveler gets stuck in the Victorian era
Length: Write a complete medium-length story of 300-500 words...
```

**Step 2**: Character Image Prompt Generation
```
Extract ONLY the visual/physical details from this character description:
[Generated character description]
Create a focused image prompt for a sci-fi character portrait...
```

**Step 3**: Background Image Prompt Generation
```
Extract ONLY the visual/environmental details from this background description:
[Generated background description]
Create a focused environment image prompt for a sci-fi setting...
```

**Step 4**: Scene Composition
- Remove character background
- Analyze positioning needs
- Composite final scene
- Apply sci-fi genre effects

### Audio-Only Generation

**Input**: Audio file describing a mystery in a small town
**Genre**: Mystery
**Length**: Long

**Step 1**: Audio Transcription
```
Whisper transcription: "There's something strange happening in the old Millbrook library. Books are moving by themselves, and the librarian won't talk about the restricted section that's been locked for decades."
```

**Step 2**: Story Generation Using Transcription
```
You are a professional storyteller and world-builder...
Genre: mystery
User Prompt: There's something strange happening in the old Millbrook library...
```

**Step 3-4**: Same image generation and composition process as text-only

### Mixed Input Generation

**Input**: 
- Text: "A magical academy"  
- Audio: Description of floating castles and spell-casting students
**Genre**: Fantasy
**Length**: Short

**Step 1**: Combined Prompt Creation
```python
combined_prompt_parts = []
if text_prompt:
    combined_prompt_parts.append(f"Text prompt: {text_prompt}")
if audio_transcription:
    combined_prompt_parts.append(f"Audio description: {audio_transcription}")

combined_prompt = " | ".join(combined_prompt_parts)
# Result: "Text prompt: A magical academy | Audio description: [transcription]"
```

**Step 2-4**: Standard story and image generation process using combined prompt

---

## Troubleshooting

### Common Prompt Issues

#### 1. Section Bleeding
**Problem**: Character descriptions appear in story section
**Solution**: The template includes explicit negative instructions:
```
- DO NOT include character descriptions or world-building details here
- Focus purely on the story events and narrative flow
```

#### 2. Parsing Failures
**Problem**: Section headers not found in LLM output
**Solution**: Multiple parsing strategies are implemented:
```python
# Primary parsing with **[SECTION]** format
story_match = re.search(r'\*\*\[STORY\]\*\*(.*?)(?=\*\*\[CHARACTER\]\*\*|$)', response, re.DOTALL | re.IGNORECASE)

# Fallback parsing without asterisks
if not story_match:
    story_match = re.search(r'\[STORY\](.*?)(?=\[CHARACTER\]|$)', response, re.DOTALL | re.IGNORECASE)
```

#### 3. Inconsistent Image Quality
**Problem**: Generated images don't match descriptions
**Solution**: Prompt cleaning removes unwanted phrases:
```python
unwanted_phrases = [
    "Visual Image Prompt:", "Image Prompt:", "Based on", "character description", 
    "This character", "The protagonist", "story", "personality", "motivation"
]

for phrase in unwanted_phrases:
    cleaned = re.sub(phrase, "", cleaned, flags=re.IGNORECASE)
```

#### 4. Audio Transcription Errors
**Problem**: Poor transcription quality affects story generation
**Solution**: Audio validation prevents problematic files:
```python
# File size validation (10MB limit)
if audio_file.size > 10 * 1024 * 1024:
    raise forms.ValidationError("Audio file must be smaller than 10MB.")

# Duration validation using pydub
audio = AudioSegment.from_file(temp_file_path)
duration = len(audio) / 1000.0
if duration > max_duration:
    return {'valid': False, 'error': f'Audio too long. Maximum duration is {max_duration/60:.1f} minutes'}
```

### Image Generation Issues

#### 1. API Failures
**Problem**: Hugging Face API returns 503 or timeout errors
**Solution**: Multiple model fallback system:
```python
# Try multiple models until one works
for model in self.hf_image_models:
    try:
        image_data = self._call_huggingface_api(model, full_prompt, image_type="portrait")
        if image_data:
            return {
                'image_data': image_data,
                'model_used': model,
                'success': True
            }
    except Exception as e:
        logger.warning(f"Failed to generate character with {model}: {e}")
        continue

# Stability.ai fallback
return self._call_stability_api(prompt, image_type=image_type)
```

#### 2. Background Removal Issues
**Problem**: Character images retain unwanted backgrounds
**Solution**: Enhanced background removal and fallback:
```python
try:
    char_img = remove(char_img)  # rembg library
except Exception as e:
    logger.warning(f"Background removal failed: {e}")
    # Continue with original image
```

#### 3. Style Inconsistency
**Problem**: Character and background images have different lighting/colors
**Solution**: Style matching algorithm:
```python
def _match_image_styles(self, char_img, bg_img, genre):
    # Analyze color temperature
    char_temp = self._calculate_color_temperature(char_array)
    bg_temp = self._calculate_color_temperature(bg_array)
    
    # Adjust if significant difference
    if abs(char_temp - bg_temp) > 500:
        char_img = self._adjust_color_temperature(char_img, bg_temp - char_temp)
```

### Performance Optimization

#### 1. Prompt Length Management
**Problem**: Very long prompts may cause processing delays
**Solution**: Character limits enforced in templates:
```python
# Character image prompt under 150 characters
"FORMAT: Create a single comma-separated prompt under 150 characters"

# Background image prompt similar constraint
"[environment type], [architectural style], [lighting/time], [weather/atmosphere]"
```

#### 2. Model Selection
**Problem**: Slow generation times
**Current Solution**: Fast models prioritized:
```python
self.hf_image_models = [
    "black-forest-labs/FLUX.1-schnell",  # Fast and free
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5"
]
```

---

## Advanced Features

### Scene Composition Details

The system performs sophisticated image composition:

#### Position Analysis
Based on character and background descriptions:
```python
position_info = {
    'char_position': 'center',      # Horizontal: center, left, right
    'char_size_factor': 0.6,        # Size relative to background (0.4-0.8)
    'char_vertical_pos': 0.7,       # Vertical: 0.0=top, 1.0=bottom
    'depth_layer': 'foreground',    # Depth: foreground, midground, background
    'interaction_type': 'standing'  # Pose: standing, sitting, action
}
```

#### Automatic Analysis
The system analyzes descriptions for positioning clues:
```python
# Extract positioning hints from descriptions
char_lower = character_desc.lower()
bg_lower = background_desc.lower()

# Size adjustment for environment scale
if any(word in bg_lower for word in ['vast', 'enormous', 'massive']):
    position_info['char_size_factor'] = 0.4  # Smaller in grand environments
elif any(word in bg_lower for word in ['intimate', 'small', 'cozy']):
    position_info['char_size_factor'] = 0.8  # Larger in small spaces
```

### Genre-Specific Processing

Each genre receives tailored treatment:

#### Visual Styles
```python
style_mapping = {
    'fantasy': 'fantasy art style, magical lighting, ethereal atmosphere',
    'sci-fi': 'science fiction art style, futuristic, cyberpunk lighting',
    'mystery': 'noir style, dramatic shadows, moody atmosphere',
    'horror': 'gothic horror style, dark atmosphere, ominous lighting'
}
```

#### Post-Processing Effects
Genre-specific image enhancement:
```python
if genre in ['horror', 'mystery']:
    # Darken and increase contrast
    enhancer = ImageEnhance.Brightness(combined_img)
    combined_img = enhancer.enhance(0.8)
    
elif genre in ['fantasy', 'adventure']:
    # Enhance colors and saturation
    enhancer = ImageEnhance.Color(combined_img)
    combined_img = enhancer.enhance(1.1)
```

### Error Handling & Fallbacks

#### Mock Data Generation
When services fail, the system provides fallback content:
```python
def _generate_mock_complete_story(self, prompt, genre):
    return {
        'story': f"""[Generated fallback story based on {genre} genre]""",
        'character_description': """[Detailed character profile with physical and personality traits]""",
        'background_description': """[Rich world-building and setting details]"""
    }
```

#### Placeholder Images
When image generation fails:
```python
def _generate_placeholder_image(self, image_type):
    return {
        'image_data': None,
        'prompt': f"{image_type.title()} image generation unavailable",
        'model_used': "placeholder",
        'success': False,
        'placeholder': True,
        'type': image_type
    }
```

### Input Validation & Processing

#### Form Validation Logic
The Django form includes sophisticated validation:
```python
def clean(self):
    cleaned_data = super().clean()
    prompt = cleaned_data.get('prompt')
    audio_file = cleaned_data.get('audio_file')
    input_type = cleaned_data.get('input_type')
    
    # Type-specific validation
    if input_type == 'text' and not prompt:
        raise forms.ValidationError("Text prompt is required when using text input.")
    
    if input_type == 'audio' and not audio_file:
        raise forms.ValidationError("Audio file is required when using audio input.")
```

#### Audio Processing Pipeline
Complete audio handling workflow:
```python
# 1. File validation
validation_result = story_service.validate_audio_file(audio_file)

# 2. Format conversion using pydub
audio = AudioSegment.from_file(temp_file_path)
duration = len(audio) / 1000.0

# 3. Whisper transcription
result = self.whisper_model.transcribe(temp_file_path)
transcription = result["text"].strip()

# 4. Metadata extraction
return {
    'transcription': transcription,
    'duration': duration,
    'language': result.get('language', 'unknown'),
    'segments': len(result.get('segments', []))
}
```