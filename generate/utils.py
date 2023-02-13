import os
import threading
import uuid

import openai
from datetime import datetime

from django.core.mail import mail_admins, EmailMessage

from dotenv import load_dotenv

from .models import *

load_dotenv()

openai.api_key = os.environ['API_AI_KEY']


def calculate_years(start_date):
    d1 = datetime.today().year
    difference = d1 - int(start_date)
    return difference


def create_prompt(info, answers, first_name):
    prompt = (f'Write a love {info.get("content_type")} '
              f'in a {info.get("style")} '
              f'style and {info.get("tone", "romantic")} tone of voice '
              f'using {info.get("length", "500")} words for '
              f'this occasion: {info.get("occasion")}. '
              f'I am a {info.get("genders")} '
              f'named {info.get("partner_name")} '
              f'who is my {info.get("relationship_type")} '
              f'for the last {calculate_years(info.get("relationship_start_date"))} years. '
              f'Sign the {info.get("content_type")} with my name: {first_name}. ')

    addition = ''
    if answers:
        questions = Questions.objects.filter(id__in=[int(x) for x in answers.keys()])
        for i in answers.items():
            d = questions.get(id=int(i[0]))
            for j in i[1]:
                if j:
                    addition += f'Try and mention that {d.prompt_text} {j} '

    final_prompt = prompt + addition
    return final_prompt


def get_ai_response(prompt):
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=2048, temperature=0)
    return response["choices"][0]["text"]


def send_ai_request(info, answers, user):
    content_type = ContentTypes.objects.filter(id=info['content_type']).first()
    info['content_type'] = content_type.title

    prompt = create_prompt(info, answers, user.first_name)
    generated_text = get_ai_response(prompt).strip("\n\n")

    title = f'Your love {info.get("content_type").lower()} to {info.get("partner_name")}'

    info['content_type'] = content_type.id

    content = Content.objects.create(
        user=user,
        content_type=content_type,
        title=title,
        text=generated_text,
        prompt=prompt,
        answers=answers,
        content_info=info
    )
    user.profile.credits_count -= content_type.credits
    user.save()

    return content.get_absolute_url()


class SendAdminEmail(threading.Thread):
    def __init__(self, subject, message):
        self.subject = subject
        self.message = message
        threading.Thread.__init__(self)

    def run(self):
        mail_admins(subject=self.subject, message=self.message)


class SendMyEmails(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.message = message
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.message, bcc=self.recipient_list)
        msg.content_subtype = "html"
        msg.send()

