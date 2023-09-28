from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


class passwordgenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp) +  six.text_type(user.is_active))
TokenGenerator = passwordgenerator()

def SendReferalMail(user, referal, target):
    email_subject = 'Referal Confirmation'
    email_body =  render_to_string('crypto/referalmail.html',{
        'user':user.first_name,
        'referal': referal.refered_by,
        'firstname': user.first_name,
        'lastname': user.last_name

    })
    email = EmailMessage(subject=email_subject, body=email_body,
        from_email='Apexfortitude <admin@apexfortitude.com>', to=[target.user.email]
        )
    email.content_subtype = 'html'
    email.send()
    