from django.contrib import admin
from .models import Survey, Question, Answer, UserAnswer

from django.contrib import admin
from django.utils.html import format_html
from .models import Survey
from django import forms
from django.forms.widgets import DateTimeInput

    
class AdminQuestion(admin.ModelAdmin):
    list_display = ('survey', 'label', 'type_field', 'help_text', 'required')
    search_fields = ('survey__name', )


class AdminAnswer(admin.ModelAdmin):
    list_display = ('question', 'get_label', 'value', 'user_answer')
    search_fields = ('question__label', 'value',)
    list_filter = ('question__survey',)

    def get_label(self, obj):
        return obj.question.label
    get_label.admin_order_field = 'question'
    get_label.short_description = 'Label'


class AdminUserAnswer(admin.ModelAdmin):
    list_display = ('survey', 'user', 'created_at', 'updated_at')


class SurveyAdminForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = "__all__"
        widgets = {
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class AdminSurvey(admin.ModelAdmin):
    list_display = ("name", "valid_until",'slug')
    list_filter = ('valid_until',)
    exclude = ['slug']
    form = SurveyAdminForm

    class Media:
        js = ('https://code.jquery.com/jquery-3.6.0.min.js',  # jQuery CDN
              'https://cdnjs.cloudflare.com/ajax/libs/jquery-datetimepicker/2.5.20/jquery.datetimepicker.full.min.js',
              '/static/css/custom_datetime.js')  # Custom JS file
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/jquery-datetimepicker/2.5.20/jquery.datetimepicker.min.css',)
        }
    
    
    


admin.site.register(Survey, AdminSurvey)
admin.site.register(Question, AdminQuestion)
admin.site.register(Answer, AdminAnswer)
admin.site.register(UserAnswer, AdminUserAnswer)

