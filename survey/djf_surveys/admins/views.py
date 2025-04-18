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
        insights = ResponseInsights(survey=self.get_object())
        context['summary'] = summary
        context['insights'] = insights
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
class AdminAnalyticsDashboardView(ContextTitleMixin, TemplateView):
    template_name = 'djf_surveys/admins/analytics.html'
    title_page = _("Analytics Dashboard")
    
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
        
        # Get recent responses
        recent_responses = UserAnswer.objects.select_related('survey', 'user').order_by('-created_at')[:10]
        
        latest_response = UserAnswer.objects.order_by('-created_at').first()
        if latest_response:
            time_since_last = timezone.now() - latest_response.created_at
            days_since_last = time_since_last.days
            context['time_since_last'] = days_since_last
        else:
            context['time_since_last'] = None
            
        # Prepare chart data
        date_labels = []
        response_counts = []
        
        for entry in daily_responses:
            date_labels.append(entry['date'].strftime('%b %d'))
            response_counts.append(entry['count'])
            
        # Top surveys chart data
        top_survey_names = []
        top_survey_counts = []
        
        for survey in top_surveys:
            top_survey_names.append(survey.name[:20] + '...' if len(survey.name) > 20 else survey.name)
            top_survey_counts.append(survey.response_count)
            
        context.update({
            'total_surveys': total_surveys,
            'active_surveys': active_surveys,
            'scheduled_surveys': scheduled_surveys,
            'expired_surveys': expired_surveys,
            'total_responses': total_responses,
            'responses_today': responses_today,
            'top_surveys': top_surveys,
            'recent_responses': recent_responses,
            'chart_data': {
                'date_labels': date_labels,
                'response_counts': response_counts,
                'top_survey_names': top_survey_names,
                'top_survey_counts': top_survey_counts,
            }
        })
        
        return context