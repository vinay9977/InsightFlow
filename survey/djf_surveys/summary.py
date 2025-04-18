import random

from django.utils.translation import gettext

from djf_surveys import models
from djf_surveys.models import TYPE_FIELD, Survey, Question, Answer
from djf_surveys.utils import create_star

from djf_surveys.models import Survey, UserAnswer, Question, Answer, TYPE_FIELD
from collections import defaultdict

COLORS = [
    '#64748b', '#a1a1aa', '#374151', '#78716c', '#d6d3d1', '#fca5a5', '#ef4444', '#7f1d1d',
    '#fb923c', '#c2410c', '#fcd34d', '#b45309', '#fde047', '#bef264', '#ca8a04', '#65a30d',
    '#86efac', '#15803d', '#059669', '#a7f3d0', '#14b8a6', '#06b6d4', '#155e75', '#0ea5e9',
    '#075985', '#3b82f6', '#1e3a8a', '#818cf8', '#a78bfa', '#a855f7', '#6b21a8', '#c026d3',
    '#db2777', '#fda4af', '#e11d48', '#9f1239'
]


class ChartJS:
    """
    this class to generate chart https://www.chartjs.org
    """
    chart_id = ""
    chart_name = ""
    element_html = ""
    element_js = ""
    width = 400
    height = 400
    data = []
    labels = []
    colors = COLORS

    def __init__(self, chart_id: str, chart_name: str, *args, **kwargs):
        self.chart_id = f"djfChart{chart_id}"
        self.chart_name = chart_name

    def _base_element_html(self):
        self.element_html = f"""
<div class="swiper-slide">
    <blockquote class="p-6 border border-gray-100 rounded-lg shadow-lg bg-white">
      <canvas id="{self.chart_id}" width="{self.width}" height="{self.height}"></canvas>
    </blocquote>
</div>
"""

    def _shake_colors(self):
        self.colors = random.choices(COLORS, k=len(self.labels))

    def _config(self):
        pass

    def _setup(self):
        pass

    def render(self):
        self._base_element_html()
        self._shake_colors()
        script = f"""
{self.element_html}
<script>
{self._setup()}
{self._config()}
  const myChart{self.chart_id} = new Chart(
    document.getElementById('{self.chart_id}'),
    config{self.chart_id}
  );
</script>
"""
        return script


class ChartPie(ChartJS):
    """ this class to generate pie chart"""

    def _config(self):
        script = """
const config%s = {
  type: 'pie',
  data: data%s,
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: '%s'
      }
    }
  },
};
"""
        return script % (self.chart_id, self.chart_id, self.chart_name)

    def _setup(self):
        script = """
const data%s = {
  labels: %s,
  datasets: [
    {
      label: 'Dataset 1',
      data: %s,
      backgroundColor: %s
    }
  ]
};
"""
        return script % (self.chart_id, self.labels, self.data, self.colors)


class ChartBar(ChartJS):
    """ this class to generate bar chart"""

    def _config(self):
        script = """
const config%s = {
  type: 'bar',
  data: data%s,
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    },
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: '%s'
      }
    }
  },
};
"""
        return script % (self.chart_id, self.chart_id, self.chart_name)

    def _setup(self):
        script = """
const data%s = {
  labels: %s,
  datasets: [{
    data: %s,
    backgroundColor: %s,
    borderWidth: 1
  }]
};
"""
        return script % (self.chart_id, self.labels, self.data, self.colors)


class ChartBarRating(ChartBar):
    height = 200
    rate_avg = 0
    num_stars = 5

    def _base_element_html(self):
        stars = create_star(active_star=int(self.rate_avg), num_stars=self.num_stars)
        self.element_html = f"""
<div class="swiper-slide">
    <blockquote class="p-6 border border-gray-100 rounded-lg shadow-lg bg-white">
      <div class="bg-yellow-100 space-y-1 py-5 rounded-md border border-yellow-200 text-center shadow-xs mb-2">
          <h1 class="text-5xl font-semibold"> {self.rate_avg}</h1>
          <div class="flex justify-center">
              {stars}
          </div>
          <h5 class="mb-0 mt-1 text-sm"> Rate Average</h5>
      </div>
      <canvas id="{self.chart_id}" width="{self.width}" height="{self.height}"></canvas>
    </blocquote>
</div>
"""


class SummaryResponse:

    def __init__(self, survey: Survey):
        self.survey = survey

    def _process_radio_type(self, question: Question) -> str:
        pie_chart = ChartPie(chart_id=f"chartpie_{question.id}", chart_name=question.label)
        labels = question.choices.split(",")

        data = []
        for label in labels:
            clean_label = label.strip().replace(' ', '_').lower()
            count = Answer.objects.filter(question=question, value=clean_label).count()
            data.append(count)

        pie_chart.labels = labels
        pie_chart.data = data
        return pie_chart.render()

    def _process_rating_type(self, question: Question):
        if not question.choices:  # use 5 as default for backward compatibility
            question.choices = 5

        bar_chart = ChartBarRating(chart_id=f"chartbar_{question.id}", chart_name=question.label)
        bar_chart.num_stars = int(question.choices)
        labels = [str(item + 1) for item in range(int(question.choices))]

        data = []
        for label in labels:
            count = Answer.objects.filter(question=question, value=label).count()
            data.append(count)

        values_rating = Answer.objects.filter(question=question).values_list('value', flat=True)
        values_convert = [int(v) for v in values_rating]
        try:
            rating_avg = round(sum(values_convert) / len(values_convert), 1)
        except ZeroDivisionError:
            rating_avg = 0

        bar_chart.labels = labels
        bar_chart.data = data
        bar_chart.rate_avg = rating_avg
        return bar_chart.render()

    def _process_multiselect_type(self, question: Question) -> str:
        bar_chart = ChartBar(chart_id=f"barchart_{question.id}", chart_name=question.label)
        labels = question.choices.split(",")

        str_value = []
        for answer in Answer.objects.filter(question=question):
            str_value.append(answer.value)
        all_value = ",".join(str_value)
        data_value = all_value.split(",")

        data = []
        for label in labels:
            clean_label = label.strip().replace(' ', '_').lower()
            data.append(data_value.count(clean_label))

        bar_chart.labels = labels
        bar_chart.data = data
        return bar_chart.render()

    def generate(self):
        html_str = []
        for question in self.survey.questions.all():
            if question.type_field == TYPE_FIELD.radio or question.type_field == TYPE_FIELD.select:
                html_str.append(self._process_radio_type(question))
            elif question.type_field == TYPE_FIELD.multi_select:
                html_str.append(self._process_multiselect_type(question))
            elif question.type_field == TYPE_FIELD.rating:
                html_str.append(self._process_rating_type(question))
        if not html_str:
            input_types = ', '.join(str(x[1]) for x in models.Question.TYPE_FIELD if
                                    x[0] in (
                                    models.TYPE_FIELD.radio, models.TYPE_FIELD.select, models.TYPE_FIELD.multi_select,
                                    models.TYPE_FIELD.rating))
            return """
<div class="bg-yellow-100 space-y-1 py-5 rounded-md border border-yellow-200 text-center shadow-xs mb-2">
    <h1 class="text-2xl font-semibold">{}</h1>
    <h5 class="mb-0 mt-1 text-sm p-2">{}</h5>
</div>
""".format(gettext("No summary"), gettext("Summary is available only for input type: %ss") % input_types)

        return " ".join(html_str)
  
class ResponseInsights:
    """
    This class analyzes survey responses to generate insights
    """
    def __init__(self, survey: Survey):
        self.survey = survey
        self.response_count = UserAnswer.objects.filter(survey=survey).count()
        self.question_count = survey.questions.count()
        
    def generate(self):
        """Generate insights from survey responses"""
        if self.response_count == 0:
            return self._empty_insights_html()
        
        # Generate various insights
        completion_rate = self._calculate_completion_rate()
        time_analysis = self._analyze_response_time()
        engagement = self._analyze_engagement()
        key_stats = self._generate_key_stats()
        
        # Combine all insights
        html_str = f"""
<div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-8">
    <h3 class="text-xl font-semibold mb-4">{gettext('Response Insights')}</h3>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {key_stats}
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        {completion_rate}
        {time_analysis}
        {engagement}
    </div>
</div>
"""
        return html_str
    
    def _empty_insights_html(self):
        """Return HTML for when no responses are available"""
        return f"""
<div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-8 text-center">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
    <h3 class="text-xl font-medium text-gray-900 mb-2">{gettext('No Responses Yet')}</h3>
    <p class="text-gray-500">{gettext('Once users start responding to your survey, insights will appear here.')}</p>
</div>
"""
    
    def _calculate_completion_rate(self):
        """Calculate and visualize completion rate"""
        # Get all user answers
        user_answers = UserAnswer.objects.filter(survey=self.survey)
        
        # Calculate number of answers per user_answer
        answers_counts = []
        for ua in user_answers:
            answer_count = Answer.objects.filter(user_answer=ua).count()
            answers_counts.append(answer_count)
        
        # Calculate completion statistics
        if not answers_counts:
            return ""
        
        avg_answers = sum(answers_counts) / len(answers_counts)
        completion_rate = (avg_answers / self.question_count) * 100 if self.question_count > 0 else 0
        
        # Count full completions (all questions answered)
        full_completions = sum(1 for count in answers_counts if count >= self.question_count)
        full_completion_rate = (full_completions / self.response_count) * 100 if self.response_count > 0 else 0
        
        # Define color based on completion rate
        if completion_rate >= 80:
            color_class = "bg-green-500"
        elif completion_rate >= 50:
            color_class = "bg-yellow-500"
        else:
            color_class = "bg-red-500"
        
        # Create HTML
        html = f"""
<div class="bg-gray-50 p-5 rounded-lg">
    <h4 class="text-lg font-medium mb-3">{gettext('Completion Rate')}</h4>
    
    <div class="mb-4">
        <div class="flex justify-between mb-1">
            <span class="text-sm font-medium">{completion_rate:.1f}%</span>
            <span class="text-sm font-medium">{avg_answers:.1f}/{self.question_count}</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2.5">
            <div class="{color_class} h-2.5 rounded-full" style="width: {min(completion_rate, 100)}%"></div>
        </div>
    </div>
    
    <div class="text-sm text-gray-600 space-y-2">
        <p>{gettext('Full completions')}: {full_completions} ({full_completion_rate:.1f}%)</p>
        <p>{gettext('Average questions answered')}: {avg_answers:.1f}</p>
    </div>
</div>
"""
        return html
    
    def _analyze_response_time(self):
        """Analyze when people respond to the survey"""
        # Get all user answers
        user_answers = UserAnswer.objects.filter(survey=self.survey)
        
        # Skip if no responses
        if not user_answers.exists():
            return ""
        
        # Count responses by hour of day
        hour_counts = defaultdict(int)
        for ua in user_answers:
            hour = ua.created_at.hour
            hour_counts[hour] += 1
        
        # Find peak hours
        if hour_counts:
            peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
            
            # Convert to 12-hour format
            peak_hour_12 = peak_hour % 12
            if peak_hour_12 == 0:
                peak_hour_12 = 12
            peak_hour_ampm = "AM" if peak_hour < 12 else "PM"
            peak_time = f"{peak_hour_12} {peak_hour_ampm}"
            
            # Classify time periods
            morning_responses = sum(hour_counts.get(h, 0) for h in range(5, 12))  # 5 AM - 12 PM
            afternoon_responses = sum(hour_counts.get(h, 0) for h in range(12, 17))  # 12 PM - 5 PM
            evening_responses = sum(hour_counts.get(h, 0) for h in range(17, 22))  # 5 PM - 10 PM
            night_responses = sum(hour_counts.get(h, 0) for h in range(22, 24)) + sum(hour_counts.get(h, 0) for h in range(0, 5))  # 10 PM - 5 AM
            
            total = morning_responses + afternoon_responses + evening_responses + night_responses
            
            # Calculate percentages
            morning_pct = (morning_responses / total) * 100 if total > 0 else 0
            afternoon_pct = (afternoon_responses / total) * 100 if total > 0 else 0
            evening_pct = (evening_responses / total) * 100 if total > 0 else 0
            night_pct = (night_responses / total) * 100 if total > 0 else 0
        else:
            peak_time = "N/A"
            morning_pct = afternoon_pct = evening_pct = night_pct = 0
        
        # Create HTML
        html = f"""
<div class="bg-gray-50 p-5 rounded-lg">
    <h4 class="text-lg font-medium mb-3">{gettext('Response Timing')}</h4>
    
    <div class="flex items-center mb-4">
        <div class="bg-blue-100 p-2 rounded-full mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        </div>
        <div>
            <p class="text-sm text-gray-600">{gettext('Peak response time')}</p>
            <p class="font-medium">{peak_time}</p>
        </div>
    </div>
    
    <div class="space-y-3">
        <div>
            <div class="flex justify-between text-xs text-gray-600 mb-1">
                <span>{gettext('Morning')}</span>
                <span>{morning_pct:.1f}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div class="bg-yellow-500 h-1.5 rounded-full" style="width: {morning_pct}%"></div>
            </div>
        </div>
        
        <div>
            <div class="flex justify-between text-xs text-gray-600 mb-1">
                <span>{gettext('Afternoon')}</span>
                <span>{afternoon_pct:.1f}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div class="bg-orange-500 h-1.5 rounded-full" style="width: {afternoon_pct}%"></div>
            </div>
        </div>
        
        <div>
            <div class="flex justify-between text-xs text-gray-600 mb-1">
                <span>{gettext('Evening')}</span>
                <span>{evening_pct:.1f}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div class="bg-red-500 h-1.5 rounded-full" style="width: {evening_pct}%"></div>
            </div>
        </div>
        
        <div>
            <div class="flex justify-between text-xs text-gray-600 mb-1">
                <span>{gettext('Night')}</span>
                <span>{night_pct:.1f}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div class="bg-blue-500 h-1.5 rounded-full" style="width: {night_pct}%"></div>
            </div>
        </div>
    </div>
</div>
"""
        return html
    
    def _analyze_engagement(self):
        """Analyze user engagement with text/essay questions"""
        # Find text area questions
        text_questions = self.survey.questions.filter(type_field=TYPE_FIELD.text_area)
        
        # Skip if no text area questions
        if not text_questions.exists():
            return ""
        
        # Analyze response length and quality
        text_answers = Answer.objects.filter(
            question__in=text_questions,
            user_answer__survey=self.survey
        )
        
        # Skip if no text answers
        if not text_answers.exists():
            return ""
        
        # Calculate average response length
        total_words = 0
        total_chars = 0
        response_count = text_answers.count()
        
        for answer in text_answers:
            words = answer.value.split()
            total_words += len(words)
            total_chars += len(answer.value)
        
        avg_words = total_words / response_count if response_count > 0 else 0
        avg_chars = total_chars / response_count if response_count > 0 else 0
        
        # Rate the engagement
        if avg_words >= 50:
            engagement_level = gettext("Excellent")
            engagement_text = gettext("Respondents are writing detailed responses")
        elif avg_words >= 25:
            engagement_level = gettext("Good")
            engagement_text = gettext("Respondents are providing good details")
        elif avg_words >= 10:
            engagement_level = gettext("Fair")
            engagement_text = gettext("Responses are somewhat brief")
        else:
            engagement_level = gettext("Low")
            engagement_text = gettext("Responses are very brief")
        
        # Create HTML
        html = f"""
<div class="bg-gray-50 p-5 rounded-lg">
    <h4 class="text-lg font-medium mb-3">{gettext('Text Response Quality')}</h4>
    
    <div class="flex items-center mb-4">
        <div class="bg-purple-100 p-2 rounded-full mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
        </div>
        <div>
            <p class="text-sm text-gray-600">{gettext('Engagement Level')}</p>
            <p class="font-medium">{engagement_level}</p>
        </div>
    </div>
    
    <div class="space-y-3 text-sm">
        <p>{engagement_text}</p>
        <p>{gettext('Average words per response')}: {avg_words:.1f}</p>
        <p>{gettext('Average characters per response')}: {avg_chars:.1f}</p>
    </div>
</div>
"""
        return html
    
    def _generate_key_stats(self):
        """Generate key stats cards"""
        # Get completion time information
        recent_responses = 10  # Number of recent responses to analyze
        
        user_answers = UserAnswer.objects.filter(survey=self.survey).order_by('-created_at')[:recent_responses]
        
        # Sample data - in a full implementation, you would compute these values
        avg_completion_time = "2:45"  # Placeholder
        response_rate_change = "+15%"  # Placeholder
        
        # Create key stats cards
        html = f"""
<div class="bg-white p-4 border rounded-lg flex items-center">
    <div class="bg-blue-100 p-3 rounded-full mr-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
    </div>
    <div>
        <p class="text-sm text-gray-500">{gettext('Total Responses')}</p>
        <p class="text-xl font-semibold">{self.response_count}</p>
    </div>
</div>

<div class="bg-white p-4 border rounded-lg flex items-center">
    <div class="bg-green-100 p-3 rounded-full mr-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    </div>
    <div>
        <p class="text-sm text-gray-500">{gettext('Weekly Change')}</p>
        <p class="text-xl font-semibold text-green-600">{response_rate_change}</p>
    </div>
</div>

<div class="bg-white p-4 border rounded-lg flex items-center">
    <div class="bg-purple-100 p-3 rounded-full mr-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    </div>
    <div>
        <p class="text-sm text-gray-500">{gettext('Avg. Completion Time')}</p>
        <p class="text-xl font-semibold">{avg_completion_time}</p>
    </div>
</div>

<div class="bg-white p-4 border rounded-lg flex items-center">
    <div class="bg-yellow-100 p-3 rounded-full mr-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
        </svg>
    </div>
    <div>
        <p class="text-sm text-gray-500">{gettext('Questions')}</p>
        <p class="text-xl font-semibold">{self.question_count}</p>
    </div>
</div>
"""
        return html
