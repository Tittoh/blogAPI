""" Core mail sender"""
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


class SendMail:
    """ Send email to user """

    def __init__(self, template_name, context, to, subject="Awesome Blog API", request=None):
        self.template_name = template_name
        self.context = context
        self.to = to
        self.subject = subject
        self.request = request

    def send(self):
        """ Send mail. """
        message = render_to_string(
            self.template_name, context=self.context, request=self.request)
        mail = EmailMessage(
            subject=self.subject, body=message, to=self.to
        )
        mail.content_subtype = "html"
        mail.send()
