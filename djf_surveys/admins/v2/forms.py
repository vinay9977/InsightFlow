from django import forms
from django.utils.translation import gettext_lazy as _
from djf_surveys.models import Question, Survey
from djf_surveys.widgets import InlineChoiceField


class QuestionForm(forms.ModelForm):
    
    class Meta:
        model = Question
        fields = ['label', 'key', 'help_text', 'required']


class QuestionWithChoicesForm(forms.ModelForm):
    
    class Meta:
        model = Question
        fields = ['label', 'key', 'choices', 'help_text', 'required']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choices'].widget = InlineChoiceField()
        self.fields['choices'].help_text = _("Click Button Add to adding choice")


class QuestionFormRatings(forms.ModelForm):
    
    class Meta:
        model = Question
        fields = ['label', 'key', 'choices', 'help_text', 'required']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choices'].widget = forms.NumberInput(attrs={'max':10, 'min':1})
        self.fields['choices'].help_text = _("Must be between 1 and 10")
        self.fields['choices'].label = _("Number of ratings")
        self.fields['choices'].initial = 5


class SurveyForm(forms.ModelForm):
    
    class Meta:
        model = Survey
        fields = [
            'name', 'description', 'editable', 'deletable', 
            'duplicate_entry', 'private_response', 'can_anonymous_user',
            'notification_to', 'success_page_content', 'start_date', 'end_date','target_responses'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notification_to'].widget = InlineChoiceField()
        # Add date/time pickers for the schedule fields
        self.fields['start_date'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
        self.fields['end_date'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Validate that end_date is after start_date if both are provided
        if start_date and end_date and start_date >= end_date:
            self.add_error('end_date', _('End date must be after start date'))
            
        return cleaned_data
