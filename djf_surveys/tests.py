from django.test import TestCase
from django.core.exceptions import ValidationError
from djf_surveys.validators import RatingValidator
from django.contrib.admin.sites import site


from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from django.core.exceptions import ValidationError

from djf_surveys.models import Survey, Question, UserAnswer, Answer, TYPE_FIELD
from djf_surveys.forms import CreateSurveyForm, EditSurveyForm
from djf_surveys import app_settings


class ValidationForm(TestCase):
    def test_validate_rating(self):
        with self.assertRaises(ValidationError):
            val = RatingValidator(10)
            val(0)

        with self.assertRaises(ValidationError):
            val = RatingValidator(10)
            val(100)

        val = RatingValidator(5)
        val(2)





class SurveyModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.survey = Survey.objects.create(
            name='Test Survey',
            description='Test Description',
            can_anonymous_user=False,
            duplicate_entry=False,
            editable=True,
            deletable=True,
            private_response=False,
            notification_to='admin@example.com'
        )

    def test_survey_slug_generation(self):
        """Test automatic slug generation"""
        survey = Survey.objects.create(name='New Test Survey')
        self.assertTrue(survey.slug)
        self.assertIn('new-test-survey', survey.slug)

    def test_duplicate_survey_slug(self):
        """Test handling of duplicate slugs"""
        survey1 = Survey.objects.create(name='Same Name')
        survey2 = Survey.objects.create(name='Same Name')
        self.assertNotEqual(survey1.slug, survey2.slug)

    def test_survey_str_representation(self):
        """Test string representation of Survey model"""
        self.assertEqual(str(self.survey), 'Test Survey')

class QuestionModelTest(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(name='Test Survey')
        self.question = Question.objects.create(
            survey=self.survey,
            label='Test Question',
            type_field=TYPE_FIELD.text,
            required=True,
            ordering=1
        )

    def test_question_key_generation(self):
        """Test automatic key generation for questions"""
        self.assertTrue(self.question.key)
        self.assertIn('test-question', self.question.key)

    def test_question_ordering(self):
        """Test question ordering"""
        q2 = Question.objects.create(
            survey=self.survey,
            label='Second Question',
            type_field=TYPE_FIELD.text,
            ordering=2
        )
        questions = Question.objects.all()
        self.assertEqual(questions[0], self.question)
        self.assertEqual(questions[1], q2)

    def test_choices_validation(self):
        """Test choices field for select/radio questions"""
        radio_question = Question.objects.create(
            survey=self.survey,
            label='Radio Question',
            type_field=TYPE_FIELD.radio,
            choices='Option 1, Option 2, Option 3'
        )
        self.assertEqual(
            len(radio_question.choices.split(',')), 
            3
        )

class AnswerModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.survey = Survey.objects.create(name='Test Survey')
        self.user_answer = UserAnswer.objects.create(
            survey=self.survey,
            user=self.user
        )
        
        # Create different types of questions and answers
        self.text_question = Question.objects.create(
            survey=self.survey,
            label='Text Question',
            type_field=TYPE_FIELD.text
        )
        self.text_answer = Answer.objects.create(
            question=self.text_question,
            value='Test Answer',
            user_answer=self.user_answer
        )
        
        self.rating_question = Question.objects.create(
            survey=self.survey,
            label='Rating Question',
            type_field=TYPE_FIELD.rating,
            choices='5'
        )
        self.rating_answer = Answer.objects.create(
            question=self.rating_question,
            value='4',
            user_answer=self.user_answer
        )
        
        self.url_question = Question.objects.create(
            survey=self.survey,
            label='URL Question',
            type_field=TYPE_FIELD.url
        )
        self.url_answer = Answer.objects.create(
            question=self.url_question,
            value='https://example.com',
            user_answer=self.user_answer
        )

    def test_answer_value_formatting(self):
        """Test value formatting for different question types"""
        # Test rating value formatting
        self.assertIn('star', self.rating_answer.get_value)
        
        # Test URL value formatting
        self.assertIn('href', self.url_answer.get_value)
        self.assertIn('https://example.com', self.url_answer.get_value)
        
        # Test text value formatting
        self.assertEqual(self.text_answer.get_value, 'Test Answer')

    def test_csv_value_formatting(self):
        """Test CSV value formatting"""
        self.assertEqual(
            self.text_answer.get_value_for_csv.strip(),
            'Test Answer'
        )

class SurveyFormTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.survey = Survey.objects.create(
            name='Test Survey',
            notification_to='admin@example.com'
        )
        
        # Create different types of questions
        self.text_question = Question.objects.create(
            survey=self.survey,
            label='Text Question',
            type_field=TYPE_FIELD.text,
            required=True
        )
        
        self.rating_question = Question.objects.create(
            survey=self.survey,
            label='Rating Question',
            type_field=TYPE_FIELD.rating,
            choices='5',
            required=True
        )
        
        self.select_question = Question.objects.create(
            survey=self.survey,
            label='Select Question',
            type_field=TYPE_FIELD.select,
            choices='Option 1, Option 2, Option 3',
            required=True
        )
        
        self.multi_select_question = Question.objects.create(
            survey=self.survey,
            label='Multi Select Question',
            type_field=TYPE_FIELD.multi_select,
            choices='Option 1, Option 2, Option 3',
            required=True
        )

    def test_create_survey_form_validation(self):
        """Test CreateSurveyForm validation"""
        form_data = {
            f'field_survey_{self.text_question.id}': 'Test Answer',
            f'field_survey_{self.rating_question.id}': '4',
            f'field_survey_{self.select_question.id}': 'option_1',
            f'field_survey_{self.multi_select_question.id}': ['option_1', 'option_2']
        }
        
        form = CreateSurveyForm(
            survey=self.survey,
            user=self.user,
            data=form_data
        )
        self.assertTrue(form.is_valid())

    def test_required_field_validation(self):
        """Test required field validation"""
        form_data = {
            f'field_survey_{self.text_question.id}': '',  # Required field empty
            f'field_survey_{self.rating_question.id}': '4',
            f'field_survey_{self.select_question.id}': 'option_1',
            f'field_survey_{self.multi_select_question.id}': ['option_1']
        }
        
        form = CreateSurveyForm(
            survey=self.survey,
            user=self.user,
            data=form_data
        )
        self.assertFalse(form.is_valid())
        self.assertIn(f'field_survey_{self.text_question.id}', form.errors)


class EditSurveyFormTest(TestCase):
    def setUp(self):
        # Similar setup as SurveyFormTest
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.survey = Survey.objects.create(
            name='Test Survey',
            editable=True
        )
        
        self.text_question = Question.objects.create(
            survey=self.survey,
            label='Text Question',
            type_field=TYPE_FIELD.text
        )
        
        self.user_answer = UserAnswer.objects.create(
            survey=self.survey,
            user=self.user
        )
        
        self.answer = Answer.objects.create(
            question=self.text_question,
            value='Original Answer',
            user_answer=self.user_answer
        )

    def test_edit_form_initial_data(self):
        """Test initial data population in edit form"""
        form = EditSurveyForm(
            user_answer=self.user_answer
        )
        self.assertEqual(
            form.fields[f'field_survey_{self.text_question.id}'].initial,
            'Original Answer'
        )

    def test_edit_form_submission(self):
        """Test edit form submission"""
        form_data = {
            f'field_survey_{self.text_question.id}': 'Updated Answer'
        }
        
        form = EditSurveyForm(
            user_answer=self.user_answer,
            data=form_data
        )
        
        self.assertTrue(form.is_valid())
        form.save()
        
        # Check that answer was updated
        self.answer.refresh_from_db()
        self.assertEqual(self.answer.value, 'Updated Answer')

class SurveyIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.survey = Survey.objects.create(
            name='Test Survey',
            can_anonymous_user=False,
            duplicate_entry=False
        )
        
        self.question = Question.objects.create(
            survey=self.survey,
            label='Test Question',
            type_field=TYPE_FIELD.text,
            required=True
        )

    def test_complete_survey_flow(self):
        """Test complete survey submission flow"""
        self.client.login(username='testuser', password='testpass123')
        
        # Submit survey
        response = self.client.post(
            reverse('djf_surveys:create', kwargs={'slug': self.survey.slug}),
            data={f'field_survey_{self.question.id}': 'Test Answer'}
        )
        self.assertEqual(response.status_code, 302)
        
        # Check answer was created
        self.assertTrue(
            Answer.objects.filter(
                question=self.question,
                value='Test Answer'
            ).exists()
        )
        
        # Try to submit again (duplicate_entry=False)
        response = self.client.get(
            reverse('djf_surveys:create', kwargs={'slug': self.survey.slug})
        )
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Edit answer
        user_answer = UserAnswer.objects.first()
        response = self.client.post(
            reverse('djf_surveys:edit', kwargs={'pk': user_answer.pk}),
            data={f'field_survey_{self.question.id}': 'Updated Answer'}
        )
        self.assertEqual(response.status_code, 302)
        
        # Check answer was updated
        self.assertTrue(
            Answer.objects.filter(
                question=self.question,
                value='Updated Answer'
            ).exists()
        )

    def test_anonymous_access(self):
        """Test anonymous access restrictions"""
        # Try to access survey (can_anonymous_user=False)
        response = self.client.get(
            reverse('djf_surveys:create', kwargs={'slug': self.survey.slug})
        )
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Set survey to allow anonymous
        self.survey.can_anonymous_user = True
        self.survey.save()
        
        # Try again
        response = self.client.get(
            reverse('djf_surveys:create', kwargs={'slug': self.survey.slug})
        )
        self.assertEqual(response.status_code, 200)  # Should allow access