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
        help_text='Describe the setting, character, or situation you want the story to be about.'
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