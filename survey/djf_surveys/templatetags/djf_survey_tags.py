from django.template import Library
from djf_surveys.utils import create_star as utils_create_star
from django.utils import timezone

register = Library()


@register.filter(name='addclass')
def addclass(field, class_attr):
    return field.as_widget(attrs={'class': class_attr})


@register.filter(name='get_id_field')
def get_id_field(field):
    parse = field.auto_id.split("_")
    return parse[-1]


@register.simple_tag
def create_star(number, id_element, num_stars):
    return utils_create_star(active_star=int(number), num_stars=num_stars, id_element=id_element)

@register.inclusion_tag('djf_surveys/components/countdown.html')
def render_countdown(survey):
    """Render a countdown for a survey based on its schedule."""
    now = timezone.now()
    
    if survey.start_date and now < survey.start_date:
        return {
            'target_date': survey.start_date,
            'survey_id': survey.id,
            'countdown_type': 'start'
        }
    elif survey.end_date and now < survey.end_date:
        return {
            'target_date': survey.end_date,
            'survey_id': survey.id,
            'countdown_type': 'end'
        }
    return {'target_date': None, 'survey_id': None, 'countdown_type': None}