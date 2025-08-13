# AI Story Generator

A Django-based web application that generates complete story packages with AI-powered text generation and visual artwork. Users can input story prompts via text, audio, or both, and receive a complete story with character portraits, environment artwork, and combined scene compositions.

## Features

### Multi-Modal Input
- **Text Input**: Traditional text-based story prompts
- **Audio Input**: Voice recordings transcribed using OpenAI Whisper
- **Mixed Input**: Combination of text and audio for richer context

### Complete Story Generation
- **Story Creation**: Full narratives with beginning, middle, and end
- **Character Development**: Detailed character descriptions and portraits
- **Environment Building**: Rich background descriptions and artwork
- **Scene Composition**: Combined scenes placing characters in environments

### AI-Powered Components
- **Text Generation**: Ollama Gemma 2B model for story and description generation
- **Audio Transcription**: OpenAI Whisper for speech-to-text conversion
- **Image Generation**: Hugging Face Inference API with Stability.ai fallback
- **Image Composition**: PIL and OpenCV for scene combination

## Architecture Overview

### Backend Structure
```
ShortStoryGenerator
├── story_generator_project
│   ├── media - to story the audio files
    ├── static
        ├── css
            └── style.css - file used for css styling
        └── js
            └── main.js - file for javascript logic of the template
    ├── story_app
        ├── models.py - StoryGeneration (Main data model)
        ├── forms.py - StoryPromptForm (Input validation)
        ├── views.py - Story generation and display logic
        ├── admin.py - Admin Access to the app
        ├── urls.py - URLs used for story generation
        └── services.py - StoryGeneratorService (Core AI integration)
    └── templates
        ├── story_app
            ├── index.html - Input interface
            └── story_result.html - Output display
        └── base.html - Layout template
```

### AI Processing Pipeline

#### Text-Only Flow
1. **Input** → Text prompt validation
2. **Story Generation** → Unified LLM call for story + descriptions
3. **Image Generation** → Character and environment images
4. **Scene Composition** → Combined final artwork
5. **Storage** → Database persistence with base64 images

#### Audio Flow
1. **Input** → Audio file upload/recording
2. **Transcription** → Whisper speech-to-text
3. **Story Generation** → Same as text flow using transcription
4. **Image Generation** → Character and environment images
5. **Scene Composition** → Combined final artwork
6. **Storage** → Database + file system for audio

#### Mixed Input Flow
1. **Input** → Text + Audio combination
2. **Processing** → Transcription + text combination
3. **Generation** → Unified prompt processing
4. **Completion** → Same as above flows

### Data Flow Architecture
```
User Input → Form Validation → Service Layer → AI Models → Database → Display
     ↓              ↓              ↓            ↓          ↓         ↓
  Text/Audio   Input Types    StoryGenerator   Ollama   Models   Templates
                              Service         Whisper
                                             HuggingFace
                                             Stability.ai
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 4.0+
- Ollama (for local LLM)
- FFmpeg (for audio processing)
- Git

### System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3-pip python3-venv ffmpeg git
```

#### macOS
```bash
brew install python ffmpeg git
```

#### Windows
- Install Python from python.org
- Install FFmpeg from ffmpeg.org
- Install Git from git-scm.com

### Application Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/sakhij/ShortStoryGenerator.git
   cd story_generator_project
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama**
   ```bash
   # Linux/macOS
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Windows - Download from ollama.com
   ```

5. **Download Ollama Model**
   ```bash
   ollama pull gemma:2b
   ```

6. **Install FFmpeg**
   ```bash
   # Linux/macOS
    sudo apt install ffmpeg
   
   # Windows
   winget install ffmpeg

7. **Environment Configuration**
   Create `.env` file in project root:
   ```env
   # Required
   HUGGINGFACE_TOKEN=your-hf-token
   STABILITY_API_KEY=your-stability-key
   
   # Database (optional - defaults to SQLite)
   DATABASE_URL=postgres://user:pass@localhost/dbname
   ```

8. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

9. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

   Visit `http://localhost:8000` to access the application.

## Configuration

### AI Model Configuration

#### Ollama Models
- **Current**: `gemma:2b` (fast, good quality)
- **Alternatives**: `llama2:7b`, `mistral:7b`

```python
# services.py
self.llm = OllamaLLM(model="gemma:2b")
```

#### Image Generation APIs
1. **Hugging Face (Free Tier)**
   - FLUX.1-schnell
   - Stable Diffusion XL
   - Stable Diffusion v1-5

2. **Stability.ai (Free for 1st 25 credits and then paid)**
   - Stable Diffusion XL 1024
   - Higher quality, faster generation

### File Storage Configuration

#### Development (Local Storage)
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### Audio Processing Configuration

#### Supported Formats
- MP3, WAV, M4A, OGG, FLAC, AAC
- Maximum size: 10MB
- Maximum duration: 5 minutes

#### Whisper Models
- `base`: Good balance (default)
- `small`: Faster, less accurate
- `large`: Slower, more accurate

## Usage Guide

### Basic Story Generation
1. Navigate to home page
2. Select "Text Only" input method
3. Enter story prompt (e.g., "A detective discovers a portal in their office")
4. Choose genre and length
5. Click "Generate Story"

### Audio Story Generation
1. Select "Audio Only" input method
2. Either upload audio file or click "Record"
3. For recording: speak your story idea clearly
4. Choose genre and length
5. Generate story

### Mixed Input
1. Select "Text + Audio" input method
2. Provide both text prompt and audio
3. System combines both inputs intelligently
4. Generate comprehensive story

### Story Management
- **View Stories**: Click on recent stories to see full details
- **Download Content**: Download audio files and scene images
- **Delete Stories**: Remove unwanted stories and associated files

## API Documentation

### StoryGeneratorService Methods

#### `generate_complete_story_with_images(prompt, length, genre)`
Generates complete story package with all components.

**Parameters:**
- `prompt` (str): Story prompt text
- `length` (str): 'short', 'medium', or 'long'
- `genre` (str): Story genre

**Returns:**
```python
{
    'story': str,
    'character_description': str,
    'background_description': str,
    'character_image': dict,
    'background_image': dict,
    'combined_scene': dict
}
```

#### `transcribe_audio(audio_file)`
Transcribes audio file to text.

**Returns:**
```python
{
    'transcription': str,
    'duration': float,
    'success': bool,
    'language': str
}
```

## Troubleshooting

### Common Issues

#### Ollama Connection Failed
```bash
# Check Ollama status
ollama list

# Restart Ollama
ollama serve

# Verify model installation
ollama pull gemma:2b
```

#### Image Generation Fails
1. Check Hugging Face API key
2. Verify internet connection
3. Models may be loading (wait 30 seconds)
4. Check Stability.ai API key for fallback

#### Audio Transcription Issues
1. Verify FFmpeg installation: `ffmpeg -version`
2. Check audio file format compatibility
3. Ensure file size < 10MB
4. Try shorter audio clips

#### Database Errors
```bash
# Reset migrations
python manage.py migrate --fake-initial

# Clear database
python manage.py flush
```

### Performance Optimization

#### For Better Speed
- Use faster Ollama models (`gemma:2b`)
- Implement Redis caching
- Use CDN for static files
- Optimize image sizes

#### For Better Quality
- Use larger Ollama models (`llama2:7b`)
- Upgrade to Stability.ai Pro
- Implement prompt refinement
- Use higher resolution images

## Acknowledgments

- **OpenAI Whisper** for audio transcription
- **Ollama** for local LLM hosting
- **Hugging Face** for free image generation API
- **Stability.ai** for high-quality image generation
- **Django** framework for web application structure

## Support

For issues and questions:
1. Check the troubleshooting section
2. Search existing GitHub issues
3. Create new issue with detailed description
4. Include logs and system information
5. Contact - [Email](mailto:sakhijain4@gmail.com)

## Updates

### Recent Changes
- Added audio input support
- Implemented scene composition
- Enhanced prompt engineering
- Improved error handling
- Added file download features

### Roadmap
- Video input support
- Multiple language support
- Real-time collaboration
- Advanced scene editing
- Mobile app development
