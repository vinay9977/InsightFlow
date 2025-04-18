from django.urls import path
from djf_surveys.admins import views as admin_views
from djf_surveys.admins.v2 import views as admin_views_v2


urlpatterns = [
    path('', admin_views.AdminSurveyListView.as_view(), name='admin_survey'),
    path('create/survey/', admin_views.AdminCrateSurveyView.as_view(), name='admin_create_survey'),
    path('edit/survey/<str:slug>/', admin_views.AdminEditSurveyView.as_view(), name='admin_edit_survey'),
    path('delete/survey/<str:slug>/', admin_views.AdminDeleteSurveyView.as_view(), name='admin_delete_survey'),
    path('forms/<str:slug>/', admin_views.AdminSurveyFormView.as_view(), name='admin_forms_survey'),
    path('question/add/<int:pk>/<int:type_field>', admin_views_v2.AdminCreateQuestionView.as_view(),
         name='admin_create_question'),
    path('question/edit/<int:pk>/', admin_views_v2.AdminUpdateQuestionView.as_view(), name='admin_edit_question'),
    path('question/delete/<int:pk>/', admin_views.AdminDeleteQuestionView.as_view(), name='admin_delete_question'),
    path('question/ordering/', admin_views.AdminChangeOrderQuestionView.as_view(), name='admin_change_order_question'),
    path('download/survey/<str:slug>/', admin_views.DownloadResponseSurveyView.as_view(), name='admin_download_survey'),
    path('summary/survey/<str:slug>/', admin_views.SummaryResponseSurveyView.as_view(), name='admin_summary_survey'),
    path('duplicate/survey/<str:slug>/', admin_views.AdminDuplicateSurveyView.as_view(), name='admin_duplicate_survey'),
     path('import/questions/<str:slug>/', admin_views.AdminImportQuestionsView.as_view(), name='admin_import_questions'),
    path('get/questions/<int:pk>/', admin_views.AdminGetSurveyQuestionsView.as_view(), name='admin_get_survey_questions'),
    path('preview/<str:slug>/', admin_views.AdminPreviewSurveyView.as_view(), name='admin_preview_survey'),
    path('questions/<slug:survey_slug>/', admin_views_v2.AdminSurveyQuestionsView.as_view(), name='admin_questions_survey'),
    path('analytics/', admin_views.AdminAnalyticsDashboardView.as_view(), name='admin_analytics_dashboard'),
]
