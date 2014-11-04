from django.core.mail import send_mail
from django.template import Context
from django.template.loader import get_template

from japper.monitoring.plugins.models import AlertSinkBase
from . import settings


class AlertSink(AlertSinkBase):

    def send_alert(self, prev_state, new_state, user=None):
        if user is None or not user.email.strip():
            return

        context = Context({
            'prev_state': prev_state,
            'new_state': new_state,
        })
        subject_template = get_template('django_email/subject.txt')
        subject = subject_template.render(context).strip()
        body_template = get_template('django_email/body.txt')
        body = body_template.render(context)
        send_mail(subject, body, settings.FROM_EMAIL, [user.email])

