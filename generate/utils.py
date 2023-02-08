import os
import threading

import openai
from datetime import datetime

from django.core.mail import mail_admins, EmailMessage
from twilio.rest import Client

from generate.models import *
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ['API_AI_KEY']

def calculate_years(start_date):
    d1 = datetime.today()

    d2 = datetime.strptime(start_date, "%Y-%m-%d")

    difference = d1.year - d2.year
    if (d1.month, d1.day) < (d2.month, d2.day):
        difference = difference - 1
    return difference

def create_prompt(info, answers, first_name):
    prompt = (f'Write a love {info.get("content_type")} '
              f'in a {info.get("letter_style") if info.get("type") != "Poem" else info.get("poem_style")} '
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
                addition += f'Try and mention that {d.prompt_text} {j}. '

    final_prompt = prompt + addition
    return final_prompt


def get_ai_response(prompt):
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=2048, temperature=0)
    return response["choices"][0]["text"]


def send_ai_request(info, answers, user):
    prompt = create_prompt(info, answers, user.first_name)
    generated_text = get_ai_response(prompt).strip("\n\n")

    title = f'Your love {info.get("content_type").lower()} to {info.get("partner_name")}'

    content = Content.objects.create(
        user=user,
        content_type=info.get('content_type').lower(),
        title=title,
        text=generated_text,
        prompt=prompt,
        answers=answers,
        content_info=info
    )
    user.profile.credits_count -= CreditsPrice.objects.get(credits_type=info.get("content_type").lower()).credits
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

    def run (self):
        msg = EmailMessage(self.subject, self.message, bcc=self.recipient_list)
        msg.content_subtype = "html"
        msg.send()


def smsnottrhes(number_to, title, text):
    number_to = str(number_to)
    client = Client(os.environ['TWILIO_SID'], os.environ['TWILIO_TOKEN'])

    final_text = f'{title}\n\n{text}'
    n = 1500  # cut characters in text
    d = [final_text[i:i + n] for i in range(0, len(final_text), n)]

    print(d)

    for i in d:
        client.messages.create(
            body=i,
            from_=os.environ['TWILIO_PHONE_NUMBER'],
            to=number_to
        )

class SmsThread(threading.Thread):
    def __init__(self, number_to, title, text):
        self.number_to = str(number_to)
        self.title = title
        self.text = text
        threading.Thread.__init__(self)

    def run(self):
        try:
            client = Client(os.environ['TWILIO_SID'], os.environ['TWILIO_TOKEN'])

            final_text = f'{self.title}\n\n{self.text}'
            n = 1500  # cut characters in text
            d = [final_text[i:i + n] for i in range(0, len(final_text), n)]


            for i in d:
                client.messages.create(
                    body=i,
                    from_=os.environ['TWILIO_PHONE_NUMBER'],
                    to=self.number_to
                )
        except Exception as e:  # work on python 3.x
            print(str(e))