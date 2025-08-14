from django import forms

class StoryPromptForm(forms.Form):
    prompt = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your story prompt here (e.g., "A mysterious door appears in an ordinary library")',
            'rows': 4,
            'maxlength': 1000
        }),
        max_length=1000,
        label='Story Prompt',
        help_text='Describe the setting, character, or situation you want the story to be about.',
        required=False
    )
    
    # Audio upload field
    audio_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'audio/*,.mp3,.wav,.m4a,.ogg',
            'id': 'audio-upload'
        }),
        label='Audio Prompt (Optional)',
        help_text='Upload an audio file describing your story idea. Supported formats: MP3, WAV, M4A, OGG (max 10MB)',
        required=False
    )
    
    # Input type selection
    input_type = forms.ChoiceField(
        choices=[
            ('text', 'Text Only'),
            ('audio', 'Audio Only'),
            ('both', 'Text + Audio')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='text',
        label='Input Method',
        required=False
    )
    
    story_length = forms.ChoiceField(
        choices=[
            ('short', 'Short (200-300 words)'),
            ('medium', 'Medium (300-500 words)'),
            ('long', 'Long (500-750 words)')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='medium',
        label='Story Length'
    )
    
    genre = forms.ChoiceField(
        choices=[
            ('fantasy', 'Fantasy'),
            ('sci-fi', 'Science Fiction'),
            ('mystery', 'Mystery'),
            ('romance', 'Romance'),
            ('adventure', 'Adventure'),
            ('horror', 'Horror'),
            ('drama', 'Drama'),
            ('comedy', 'Comedy')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='fantasy',
        label='Genre'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        prompt = cleaned_data.get('prompt')
        audio_file = cleaned_data.get('audio_file')
        input_type = cleaned_data.get('input_type')
        
        # Validation logic
        if input_type == 'text' and not prompt:
            raise forms.ValidationError("Text prompt is required when using text input.")
        
        if input_type == 'audio' and not audio_file:
            raise forms.ValidationError("Audio file is required when using audio input.")
        
        if input_type == 'both' and not (prompt or audio_file):
            raise forms.ValidationError("At least one input method (text or audio) is required.")
        
        # File size validation
        if audio_file:
            if audio_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Audio file must be smaller than 10MB.")
        
        return cleaned_data