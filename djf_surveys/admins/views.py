import csv
from io import StringIO

from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.contrib import messages

from djf_surveys.app_settings import SURVEYS_ADMIN_BASE_PATH
from djf_surveys.models import Survey, Question, UserAnswer
from djf_surveys.mixin import ContextTitleMixin
from djf_surveys.views import SurveyListView
from djf_surveys.forms import BaseSurveyForm
from djf_surveys.summary import SummaryResponse
from djf_surveys.admins.v2.forms import SurveyForm

from django.db import models
from django.utils.translation import gettext, gettext_lazy as _
from django.db.models import Count, F, Sum, Avg
from django.utils import timezone
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.views.generic import TemplateView
import json
from collections import defaultdict
from datetime import timedelta
from djf_surveys.summary import SummaryResponse, ResponseInsights
from djf_surveys.models import Survey, UserAnswer, Question, Answer, TYPE_FIELD


@method_decorator(staff_member_required, name='dispatch')
class AdminCrateSurveyView(ContextTitleMixin, CreateView):
    template_name = 'djf_surveys/admins/form.html'
    form_class = SurveyForm
    title_page = _("Add New Survey")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            survey = form.save()
            self.success_url = reverse("djf_surveys:admin_forms_survey", args=[survey.slug])
            messages.success(self.request, gettext("%(page_action_name)s succeeded.") % dict(page_action_name=capfirst(self.title_page.lower())))
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


@method_decorator(staff_member_required, name='dispatch')
class AdminEditSurveyView(ContextTitleMixin, UpdateView):
    model = Survey
    form_class = SurveyForm
    template_name = 'djf_surveys/admins/form.html'
    title_page = _("Edit Survey")

    def get_success_url(self):
        survey = self.get_object()
        return reverse("djf_surveys:admin_forms_survey", args=[survey.slug])


@method_decorator(staff_member_required, name='dispatch')
class AdminSurveyListView(SurveyListView):
    template_name = 'djf_surveys/admins/survey_list.html'


@method_decorator(staff_member_required, name='dispatch')
class AdminSurveyFormView(ContextTitleMixin, FormMixin, DetailView):
    model = Survey
    template_name = 'djf_surveys/admins/form_preview.html'
    form_class = BaseSurveyForm

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(survey=self.object, user=self.request.user, **self.get_form_kwargs())

    def get_title_page(self):
        return self.object.name

    def get_sub_title_page(self):
        return self.object.description


@method_decorator(staff_member_required, name='dispatch')
class AdminDeleteSurveyView(DetailView):
    model = Survey

    def get(self, request, *args, **kwargs):
        survey = self.get_object()
        survey.delete()
        messages.success(request, gettext("Survey %ss succesfully deleted.") % survey.name)
        return redirect("djf_surveys:admin_survey")


@method_decorator(staff_member_required, name='dispatch')
class AdminCreateQuestionView(ContextTitleMixin, CreateView):
    """
    Note: This class already has version 2
    """
    model = Question
    template_name = 'djf_surveys/admins/question_form.html'
    success_url = reverse_lazy("djf_surveys:")
    fields = ['label', 'key', 'type_field', 'choices', 'help_text', 'required']
    title_page = _("Add Question")
    survey = None

    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = self.survey
            question.save()
            messages.success(self.request, gettext("%(page_action_name)s succeeded.") % dict(page_action_name=capfirst(self.title_page.lower())))
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("djf_surveys:admin_forms_survey", args=[self.survey.slug])


@method_decorator(staff_member_required, name='dispatch')
class AdminUpdateQuestionView(ContextTitleMixin, UpdateView):
    """
    Note: This class already has version 2
    """
    model = Question
    template_name = 'djf_surveys/admins/question_form.html'
    success_url = SURVEYS_ADMIN_BASE_PATH
    fields = ['label', 'key', 'type_field', 'choices', 'help_text', 'required']
    title_page = _("Add Question")
    survey = None

    def dispatch(self, request, *args, **kwargs):
        question = self.get_object()
        self.survey = question.survey
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("djf_surveys:admin_forms_survey", args=[self.survey.slug])


@method_decorator(staff_member_required, name='dispatch')
class AdminDeleteQuestionView(DetailView):
    model = Question
    survey = None

    def dispatch(self, request, *args, **kwargs):
        question = self.get_object()
        self.survey = question.survey
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        question = self.get_object()
        question.delete()
        messages.success(request, gettext("Question %ss succesfully deleted.") % question.label)
        return redirect("djf_surveys:admin_forms_survey", slug=self.survey.slug)


@method_decorator(staff_member_required, name='dispatch')
class AdminChangeOrderQuestionView(View):
    def post(self, request, *args, **kwargs):
        ordering = request.POST['order_question'].split(",")
        for index, question_id in enumerate(ordering):
            if question_id:
                question = Question.objects.get(id=question_id)
                question.ordering = index
                question.save()

        data = {
            'message': gettext("Update ordering of questions succeeded.")
        }
        return JsonResponse(data, status=200)


@method_decorator(staff_member_required, name='dispatch')
class DownloadResponseSurveyView(DetailView):
    model = Survey

    def get(self, request, *args, **kwargs):
        survey = self.get_object()
        user_answers = UserAnswer.objects.filter(survey=survey)
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        rows = []
        header = []
        for index, user_answer in enumerate(user_answers):
            if index == 0:
                header.append('user')
                header.append('update_at')

            rows.append(user_answer.user.username if user_answer.user else 'no auth')
            rows.append(user_answer.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
            for answer in user_answer.answer_set.all():
                if index == 0:
                    header.append(answer.question.label)
                rows.append(answer.get_value_for_csv)

            if index == 0:
                writer.writerow(header)
            writer.writerow(rows)
            rows = []

        response = HttpResponse(csv_buffer.getvalue(), content_type="text/csv")
        response['Content-Disposition'] = f'attachment; filename={survey.slug}.csv'
        return response


@method_decorator(staff_member_required, name='dispatch')
class SummaryResponseSurveyView(ContextTitleMixin, DetailView):
    model = Survey
    template_name = "djf_surveys/admins/summary.html"
    title_page = _("Summary")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summary = SummaryResponse(survey=self.get_object())
        context['summary'] = summary
        return context
    
@method_decorator(staff_member_required, name='dispatch')
class AdminDuplicateSurveyView(View):
    def get(self, request, *args, **kwargs):
        # Get the original survey
        original_survey = get_object_or_404(Survey, slug=kwargs['slug'])
        
        # Create a new survey as a copy
        new_survey = Survey.objects.create(
            name=f"{original_survey.name} (Copy)",
            description=original_survey.description,
            editable=original_survey.editable,
            deletable=original_survey.deletable,
            duplicate_entry=original_survey.duplicate_entry,
            private_response=original_survey.private_response,
            can_anonymous_user=original_survey.can_anonymous_user,
            notification_to=original_survey.notification_to,
            success_page_content=original_survey.success_page_content
        )
        
        # Copy all questions
        for question in original_survey.questions.all():
            Question.objects.create(
                survey=new_survey,
                label=question.label,
                type_field=question.type_field,
                choices=question.choices,
                help_text=question.help_text,
                required=question.required,
                ordering=question.ordering
            )
        
        messages.success(request, gettext("Survey '%s' has been successfully duplicated.") % original_survey.name)
        return redirect("djf_surveys:admin_forms_survey", slug=new_survey.slug)

@method_decorator(staff_member_required, name='dispatch')
class AdminImportQuestionsView(ContextTitleMixin, DetailView):  # Remove FormMixin
    model = Survey
    template_name = 'djf_surveys/admins/import_questions.html'
    title_page = _("Import Questions")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_survey = self.get_object()
        # Get all other surveys except the current one
        context['other_surveys'] = Survey.objects.exclude(id=current_survey.id)
        return context
    
    def post(self, request, *args, **kwargs):
        current_survey = self.get_object()
        question_ids = request.POST.getlist('question_ids')
        source_survey_id = request.POST.get('source_survey')
        
        if not source_survey_id or not question_ids:
            messages.error(request, gettext("Please select a survey and at least one question."))
            return redirect("djf_surveys:admin_import_questions", slug=current_survey.slug)
        
        # Get max ordering in current survey
        max_ordering = current_survey.questions.aggregate(models.Max('ordering'))['ordering__max'] or 0
        
        # Import selected questions
        imported_count = 0
        for idx, question_id in enumerate(question_ids):
            original_question = get_object_or_404(Question, id=question_id)
            
            # Create a new question based on the original
            Question.objects.create(
                survey=current_survey,
                label=original_question.label,
                type_field=original_question.type_field,
                choices=original_question.choices,
                help_text=original_question.help_text,
                required=original_question.required,
                ordering=max_ordering + idx + 1  # Preserve ordering but append after existing questions
            )
            imported_count += 1
        
        messages.success(request, gettext("Successfully imported %d questions.") % imported_count)
        return redirect("djf_surveys:admin_forms_survey", slug=current_survey.slug)

@method_decorator(staff_member_required, name='dispatch')
class AdminGetSurveyQuestionsView(View):
    def get(self, request, *args, **kwargs):
        survey_id = kwargs.get('pk')
        survey = get_object_or_404(Survey, id=survey_id)
        
        # Get questions data
        questions = []
        for question in survey.questions.all().order_by('ordering'):
            questions.append({
                'id': question.id,
                'label': question.label,
                'type_field': question.get_type_field_display(),
                'required': question.required
            })
        
        return JsonResponse({'questions': questions})
    
@method_decorator(staff_member_required, name='dispatch')
class AdminPreviewSurveyView(ContextTitleMixin, FormMixin, DetailView):
    model = Survey
    template_name = 'djf_surveys/admins/preview_survey.html'
    form_class = BaseSurveyForm
    title_page = _("Survey Preview")
    
    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(survey=self.object, user=self.request.user, **self.get_form_kwargs())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_preview'] = True
        context['question_count'] = self.object.questions.count()
        return context
    
    def get_title_page(self):
        return _("Preview: {}").format(self.object.name)
    
    def get_sub_title_page(self):
        return self.object.description
    
    def post(self, request, *args, **kwargs):
        """Handle form submission in preview mode (don't save data)"""
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            messages.success(
                self.request, 
                gettext("Preview submission successful. In normal mode, this submission would be saved.")
            )
            return redirect(request.path)
        else:
            messages.error(self.request, gettext("Form validation failed. Please correct the errors."))
            return self.form_invalid(form)
        
@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(ContextTitleMixin, TemplateView):
    template_name = 'djf_surveys/admins/dashboard.html'
    title_page = _("Survey Dashboard")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get key metrics
        now = timezone.now()
        
        # Survey stats
        total_surveys = Survey.objects.count()
        active_surveys = Survey.objects.filter(
            models.Q(start_date__isnull=True) | models.Q(start_date__lte=now),
            models.Q(end_date__isnull=True) | models.Q(end_date__gt=now)
        ).count()
        scheduled_surveys = Survey.objects.filter(start_date__gt=now).count()
        expired_surveys = Survey.objects.filter(end_date__lte=now).count()
        
        # Response stats
        total_responses = UserAnswer.objects.count()
        responses_today = UserAnswer.objects.filter(created_at__date=now.date()).count()
        
        # Get responses over time (last 30 days)
        thirty_days_ago = now - timezone.timedelta(days=30)
        daily_responses = UserAnswer.objects.filter(
            created_at__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Get top surveys by responses
        top_surveys = Survey.objects.annotate(
            response_count=Count('useranswer')
        ).order_by('-response_count')[:5]
        
        
        latest_response = UserAnswer.objects.order_by('-created_at').first()
        if latest_response:
            time_since_last = timezone.now() - latest_response.created_at
            days_since_last = time_since_last.days
            context['time_since_last'] = days_since_last
        else:
            context['time_since_last'] = None
        
        # Get recent activity
        recent_responses = UserAnswer.objects.select_related(
            'survey', 'user'
        ).order_by('-created_at')[:10]
        
        # Add to context
        context.update({
            'total_surveys': total_surveys,
            'active_surveys': active_surveys,
            'scheduled_surveys': scheduled_surveys,
            'expired_surveys': expired_surveys,
            'total_responses': total_responses,
            'responses_today': responses_today,
            'daily_responses': daily_responses,
            'top_surveys': top_surveys,
            'recent_responses': recent_responses,
        })
        
        return context
    
@method_decorator(staff_member_required, name='dispatch')
class AdminAnalyticsDashboardView(ContextTitleMixin, TemplateView):
    template_name = 'djf_surveys/admins/analytics_dashboard.html'
    title_page = _("Analytics Dashboard")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        survey_id = self.request.GET.get('survey_id')
        date_range = self.request.GET.get('date_range', '30')  # Default 30 days
        
        # Time range filters
        now = timezone.now()
        
        if date_range == '7':
            start_date = now - timedelta(days=7)
        elif date_range == '30':
            start_date = now - timedelta(days=30)
        elif date_range == '90':
            start_date = now - timedelta(days=90)
        elif date_range == '365':
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)  # Default
        
        # Basic filter
        filters = {'created_at__gte': start_date}
        
        # Add survey filter if provided
        if survey_id:
            try:
                survey = Survey.objects.get(id=survey_id)
                filters['survey'] = survey
                context['selected_survey'] = survey
            except Survey.DoesNotExist:
                pass
        
        # Get user answers based on filters
        user_answers = UserAnswer.objects.filter(**filters)
        
        # Response trends over time
        if date_range in ['7', '30']:
            # Daily grouping for shorter periods
            time_series = user_answers.annotate(
                period=TruncDate('created_at')
            ).values('period').annotate(
                count=Count('id')
            ).order_by('period')
            
            date_format = '%b %d'
        elif date_range == '90':
            # Weekly grouping for medium periods
            time_series = user_answers.annotate(
                period=TruncWeek('created_at')
            ).values('period').annotate(
                count=Count('id')
            ).order_by('period')
            
            date_format = '%b %d'
        else:
            # Monthly grouping for longer periods
            time_series = user_answers.annotate(
                period=TruncMonth('created_at')
            ).values('period').annotate(
                count=Count('id')
            ).order_by('period')
            
            date_format = '%b %Y'
        
        # Format for chart
        time_labels = [entry['period'].strftime(date_format) for entry in time_series]
        time_values = [entry['count'] for entry in time_series]
        
        # Demographic analysis - if demographic questions exist
        demographic_data = {}
        
        if survey_id:
            # Look for potential demographic questions (radio/select with common demographic options)
            demographic_questions = Question.objects.filter(
                survey_id=survey_id,
                type_field__in=[TYPE_FIELD.radio, TYPE_FIELD.select]
            )
            
            for question in demographic_questions:
                choices = question.choices.lower() if question.choices else ""
                
                # Identify potential demographic questions by their choices
                is_demographic = any(keyword in choices for keyword in [
                    'gender', 'age', 'education', 'income', 'occupation', 
                    'region', 'country', 'male', 'female'
                ])
                
                if is_demographic:
                    # Get distribution of answers
                    answers = Answer.objects.filter(
                        question=question, 
                        user_answer__in=user_answers
                    ).values('value').annotate(
                        count=Count('id')
                    ).order_by('-count')
                    
                    # Format for chart
                    demographic_data[question.label] = {
                        'labels': [a['value'].replace('_', ' ').capitalize() for a in answers],
                        'values': [a['count'] for a in answers]
                    }
        
        # Cross-question analysis
        cross_question_data = {}
        
        if survey_id:
            # Get key questions for potential correlations
            rating_questions = Question.objects.filter(
                survey_id=survey_id,
                type_field=TYPE_FIELD.rating
            )
            
            select_questions = Question.objects.filter(
                survey_id=survey_id,
                type_field__in=[TYPE_FIELD.radio, TYPE_FIELD.select]
            )
            
            if rating_questions.exists() and select_questions.exists():
                # Pick first rating question and first select question for analysis
                rating_q = rating_questions.first()
                select_q = select_questions.first()
                
                # Get all answers
                rating_answers = Answer.objects.filter(
                    question=rating_q,
                    user_answer__in=user_answers
                ).select_related('user_answer')
                
                select_answers = Answer.objects.filter(
                    question=select_q,
                    user_answer__in=user_answers
                ).select_related('user_answer')
                
                # Create lookup dictionary
                select_by_user_answer = {a.user_answer_id: a.value for a in select_answers}
                
                # Group rating values by select options
                correlation_data = defaultdict(list)
                
                for rating_answer in rating_answers:
                    user_answer_id = rating_answer.user_answer_id
                    if user_answer_id in select_by_user_answer:
                        select_value = select_by_user_answer[user_answer_id]
                        try:
                            rating_value = int(rating_answer.value)
                            correlation_data[select_value].append(rating_value)
                        except (ValueError, TypeError):
                            continue
                
                # Calculate average rating for each select option
                cross_question_data = {
                    'title': f"{select_q.label} vs {rating_q.label}",
                    'labels': [],
                    'values': []
                }
                
                for select_value, ratings in correlation_data.items():
                    if ratings:
                        avg_rating = sum(ratings) / len(ratings)
                        display_value = select_value.replace('_', ' ').capitalize()
                        cross_question_data['labels'].append(display_value)
                        cross_question_data['values'].append(round(avg_rating, 1))
        
        # Get all surveys for filter dropdown
        all_surveys = Survey.objects.all()
        
        # Calculate completion rates
        completion_data = {}
        
        if survey_id:
            survey = Survey.objects.get(id=survey_id)
            total_questions = survey.questions.count()
            
            if total_questions > 0:
                # Group user answers by number of answered questions
                user_answer_ids = user_answers.values_list('id', flat=True)
                
                answer_counts = Answer.objects.filter(
                    user_answer_id__in=user_answer_ids
                ).values('user_answer_id').annotate(
                    count=Count('id')
                )
                
                # Calculate completion rates
                completion_count = {
                    'complete': 0,  # 100%
                    'partial': 0,   # 50-99%
                    'minimal': 0    # <50%
                }
                
                for answer_count in answer_counts:
                    count = answer_count['count']
                    completion_pct = (count / total_questions) * 100
                    
                    if completion_pct >= 100:
                        completion_count['complete'] += 1
                    elif completion_pct >= 50:
                        completion_count['partial'] += 1
                    else:
                        completion_count['minimal'] += 1
                
                completion_data = {
                    'labels': ['Complete', 'Partial', 'Minimal'],
                    'values': [
                        completion_count['complete'],
                        completion_count['partial'],
                        completion_count['minimal']
                    ]
                }
        
        # Add to context
        context.update({
            'all_surveys': all_surveys,
            'date_range': date_range,
            'total_responses': user_answers.count(),
            'time_series': {
                'labels': time_labels,
                'values': time_values,
            },
            'demographic_data': demographic_data,
            'cross_question_data': cross_question_data,
            'completion_data': completion_data,
        })

        if survey_id:
            survey = Survey.objects.get(id=survey_id)
            
            # 1. Question Performance Analysis
            questions = Question.objects.filter(survey=survey)
            question_stats = []
            
            for question in questions:
                # Calculate completion rate for this question
                total_responses = user_answers.count()
                answered_count = Answer.objects.filter(
                    question=question,
                    user_answer__in=user_answers
                ).count()
                
                if total_responses > 0:
                    completion_rate = (answered_count / total_responses) * 100
                else:
                    completion_rate = 0
                    
                # For multiple choice questions, get answer distribution
                answer_distribution = None
                if question.type_field in [TYPE_FIELD.radio, TYPE_FIELD.select, TYPE_FIELD.multi_select]:
                    answers = Answer.objects.filter(
                        question=question,
                        user_answer__in=user_answers
                    )
                    
                    # Count frequencies of each option
                    option_counts = defaultdict(int)
                    for answer in answers:
                        options = answer.value.split(',')
                        for opt in options:
                            option_counts[opt.strip()] += 1
                            
                    answer_distribution = {
                        'labels': list(option_counts.keys()),
                        'values': list(option_counts.values())
                    }
                
                question_stats.append({
                    'question': question,
                    'completion_rate': completion_rate,
                    'answer_distribution': answer_distribution
                })
            
            # 2. Text Response Analysis (for text/textarea fields)
            text_questions = questions.filter(type_field__in=[TYPE_FIELD.text, TYPE_FIELD.text_area])
            text_analysis = []
            
            for question in text_questions:
                answers = Answer.objects.filter(
                    question=question,
                    user_answer__in=user_answers
                )
                
                # Calculate average response length
                total_words = 0
                total_chars = 0
                
                for answer in answers:
                    words = answer.value.split()
                    total_words += len(words)
                    total_chars += len(answer.value)
                
                avg_words = total_words / answers.count() if answers.count() > 0 else 0
                avg_chars = total_chars / answers.count() if answers.count() > 0 else 0
                
                text_analysis.append({
                    'question': question,
                    'avg_words': avg_words,
                    'avg_chars': avg_chars,
                    'response_count': answers.count()
                })
            
            # 3. Response Timing Analysis
            time_of_day = defaultdict(int)
            for ua in user_answers:
                hour = ua.created_at.hour
                time_of_day[hour] += 1
            
            peak_hour = max(time_of_day.items(), key=lambda x: x[1])[0] if time_of_day else None
            
            # Add to context
            context.update({
                'question_stats': question_stats,
                'text_analysis': text_analysis,
                'peak_hour': peak_hour,
                'time_of_day_data': {
                    'labels': list(time_of_day.keys()),
                    'values': list(time_of_day.values())
                }
            })
            
        return context


@method_decorator(staff_member_required, name='dispatch')
class SummaryResponseSurveyView(ContextTitleMixin, DetailView):
    model = Survey
    template_name = "djf_surveys/admins/summary.html"
    title_page = _("Summary")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summary = SummaryResponse(survey=self.get_object())
        insights = ResponseInsights(survey=self.get_object())
        context['summary'] = summary
        context['insights'] = insights
        return context