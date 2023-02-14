import json
import os
import uuid

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.core.mail import mail_admins
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, CreateView, DetailView, ListView
from django.forms.models import model_to_dict

from generate.forms import *
from generate.models import *
from generate.utils import *


class WelcomeView(TemplateView):
    template_name = 'generate/welcome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Welcome'

        context['SCRIPT'] = ScriptsHead.objects.first()

        if self.request.user.is_authenticated:
            context['url_copy'] = f'{self.request.build_absolute_uri(reverse("register"))}?referral={self.request.user.profile.referral_code}'
        else:
            context['url_copy'] = self.request.build_absolute_uri(reverse("welcome"))

        return context


class LoginUser(LoginView):
    template_name = 'generate/login.html'
    form_class = LoginUserForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('generate')
        return super(LoginUser, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['SCRIPT'] = ScriptsHead.objects.first()
        context['title'] = 'Login'
        return context

    def form_valid(self, form):
        # user = form.get_user()
        if not self.request.POST.get('remember', None):
            self.request.session.set_expiry(0)
        # if not user.profile.email_verify:
        #     messages.error(self.request, 'Please verify your email')
        #     return redirect('login')
        # else:
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('generate')


def logout_user(request):
    logout(request)
    return redirect('welcome')


class RegisterUser(CreateView):
    template_name = 'generate/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('generate')
        return super(RegisterUser, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'
        context['SCRIPT'] = ScriptsHead.objects.first()

        return context


    def post(self, request, *args, **kwargs):
        form = RegisterUserForm(self.request.POST)
        print(request.GET)
        if form.is_valid():
            user = form.save()

            auth_token = generate_auth_token()

            profile = Profile.objects.get_or_create(user=user)
            profile[0].email_code = auth_token


            if request.GET.get('referral'):
                k = Profile.objects.get(referral_code=request.GET.get('referral'))
                if k:
                    profile[0].credits_count += int(os.environ.get('REFERRAL_NEW_USER_CREDITS_PLUS', 200))
                    k.credits_count += int(os.environ.get('REFERRAL_OLD_USER_CREDITS_PLUS', 200))
                    k.save()

            profile[0].save()

            # send_email_verify(user.email, auth_token)
            # messages.success(request, 'An email has been sent to your email. Please verify your email address')
            return redirect('login')
        else:
            return render(request, self.template_name, {'form': form})


def send_email_verify(email, token):
    subject = 'Your accounts need to be verified'

    message = 'Hi! Paste the link to verify your account <br><br>'
    if os.environ.get("WEBSITE_HOSTNAME"):
        message += f'https://{os.environ.get("CUSTOM_HOSTNAME", os.environ.get("WEBSITE_HOSTNAME"))}/verify/{token}'
    else:
        message += f'http://127.0.0.1:8000/verify/{token}'

    recipient_list = [email]
    SendMyEmails(subject, message, recipient_list).start()

def verify(request, email_code):
    try:
        profile = Profile.objects.filter(email_code=email_code).first()
    except:
        messages.error(request, 'Something went wrong')
        return redirect('login')

    if profile:
        if profile.email_verify:
            messages.success(request, 'Your email has already been verified')
            return redirect('login')
        profile.email_verify = True
        profile.save()
        messages.success(request, 'Your account has been successfully verified')
    else:
        messages.error(request, 'Something went wrong')

    return redirect('login')


class GenerateView(FormView):
    template_name = 'generate/generate.html'
    form_class = GenerateForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return super(GenerateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Generate'

        context['SCRIPT'] = ScriptsHead.objects.first()

        context['get_items'] = self.request.session.get('generate_info', {})
        if not context['get_items']:
            context['get_items'] = self.request.user.profile.save_answers.get('form_answers', {})

        if not context['get_items'].get('partner_name'):
            context['get_items']['partner_name'] = self.request.user.profile.partner_name

        context['content_types'] = ContentTypes.objects.all()
        if context['get_items'].get('content_type'):
            context['current_content_type'] = context['content_types'].get(id=context['get_items'].get('content_type')).title

        context['styles'] = ContentStyles.objects.all()
        context['tone'] = Tone.objects.all()
        context['occasion'] = Occasion.objects.all()
        context['relationship_types'] = RelationshipTypes.objects.all()
        context['relationship_date'] = [datetime.today().year - i for i in range(80)]

        context['url_copy'] = f'{self.request.build_absolute_uri(reverse("register"))}?referral={self.request.user.profile.referral_code}'

        context['paypal'] = os.getenv('PAYPAL_KEY')

        d = CreditsBuyPriceAndCount.objects.last()
        context['credits_buy'] = d if d else {'credits_count': 50, 'price': 2.00}

        context['archive'] = Content.objects.filter(user=self.request.user).order_by('-time_create')[:5]

        return context

    def post(self, request, *args, **kwargs):
        form = GenerateForm({k: v for k, v in request.POST.items() if k not in {'csrfmiddlewaretoken'}})
        if form.is_valid():
            if (request.POST.get('content_type') and request.POST.get('occasion') and request.POST.get('tone') and
                    request.POST.get('genders') and request.POST.get('relationship_type')):
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if self.request.user.profile.credits_count < ContentTypes.objects.filter(
                id=self.request.POST.get('content_type')).first().credits:
            messages.error(self.request, "Sorry, you don't have enough credits")
            return redirect('generate')
        else:
            self.request.session['generate_info'] = {k: v for k, v in self.request.POST.items() if
                                                     k not in {'csrfmiddlewaretoken'}}
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please, provide data before submitting the form.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('questions')


class QuestionsView(TemplateView):
    template_name = 'generate/questions.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        if not request.session.get('generate_info'):
            return redirect('generate')
        return super(QuestionsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Questions'

        context['SCRIPT'] = ScriptsHead.objects.first()

        print(self.request.session['generate_info'])

        context['questions'] = Questions.objects.filter(is_publish=True,
                                                         content_type=self.request.session['generate_info'].get('content_type')).prefetch_related('answers_set')
        context['saved_answers'] = self.request.user.profile.save_answers.get('answers', [])
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('save'):
            answers = []
            form_answers = request.session.get('generate_info')
            for i in dict(request.POST).items():
                try:
                    int(i[0])
                    answers += i[1]
                except:
                    pass
            request.user.profile.save_answers = {'answers': answers, 'form_answers': form_answers}
            request.user.profile.save()
            messages.success(request, 'All answers are saved')
            return redirect('generate')
        else:
            dict_answers = {k: v for k, v in dict(self.request.POST).items() if k not in {'csrfmiddlewaretoken',
                                                                                          'finish', 'save'}}
            ss = send_ai_request(request.session.get('generate_info'),
                                 dict_answers,
                                 request.user)
            return redirect(ss)


class ContentView(DetailView):
    model = Content
    template_name = 'generate/content.html'
    pk_url_kwarg = 'content_id'
    context_object_name = 'content'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return super(ContentView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['content'].title
        context['ADD_FLOWER_LINK'] = os.environ.get('ADD_FLOWER_LINK')

        context['SCRIPT'] = ScriptsHead.objects.first()

        context['length'] = Length.objects.all()
        context['tones'] = Tone.objects.all()
        context['styles'] = ContentStyles.objects.filter(content_type=kwargs['object'].content_type)

        context['answers_count'] = len(context['content'].answers.keys())
        context['questions_count'] = Questions.objects.filter(content_type=context['content'].content_type).count()

        return context

    def post(self, request, *args, **kwargs):
        print(request.POST)
        if request.POST.get('length') or request.POST.get('style') or request.POST.get('tone'):
            if self.request.user.profile.credits_count < ContentTypes.objects.filter(
                    id=request.POST.get('content_type')).first().credits:
                messages.error(request, "Sorry, you don't have enough credits")
                return redirect('generate')

            content = Content.objects.get(id=self.kwargs.get('content_id'))
            dict_info_content = content.content_info
            dict_info_content['content_type'] = content.content_type.id
            dict_info_content['length'] = request.POST.get('length')
            dict_info_content['tones'] = request.POST.get('tones')
            dict_info_content['style'] = request.POST.get('style')

            ss = send_ai_request(dict_info_content,
                                 Content.objects.get(id=kwargs['content_id']).answers,
                                 request.user)
            return redirect(ss)

        return redirect(request.path)


class ArchiveView(ListView):
    model = Content
    context_object_name = 'archive'
    template_name = 'generate/archive.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Archive'
        context['SCRIPT'] = ScriptsHead.objects.first()
        context['ordering'] = {
            '-time_create': 'Latest first',
            'time_create': 'Oldest first',
            'title': 'A -> Z',
            '-title': 'Z -> A',
            'content_type': 'Type A -> Z',
            '-content_type': 'Type Z <- A',
        }
        context['get_items'] = self.request.GET

        return context

    def get_queryset(self):
        queryset = Content.objects.filter(user=self.request.user).order_by('-time_create')
        if self.request.GET.get('order_by'):
            queryset = queryset.order_by(self.request.GET.get('order_by'))
        return queryset


def change_questions(request, content_id):
    content = Content.objects.get(id=content_id)
    if request.user.profile.credits_count < content.content_type.credits:
        messages.error(request, "Sorry, you don't have enough credits")
        return redirect('generate')
    else:
        request.session['generate_info'] = content.content_info

    return redirect('questions')


def completeTransation(request):
    body = json.loads(request.body)
    request.user.profile.credits_count += body.get('credits', 0)
    request.user.profile.save()

    Transactions.objects.create(
        user=request.user,
        credits_count=body.get('credits', 0),
        price=body.get('price', 0)
    )
    return JsonResponse({'credits': request.user.profile.credits_count})


class AccountView(FormView):
    template_name = 'generate/account.html'
    form_class = AccountForm
    success_url = reverse_lazy('account')

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return super(AccountView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AccountView, self).get_form_kwargs()

        user_dict = model_to_dict(self.request.user)
        profile_dict = model_to_dict(self.request.user.profile)

        info = {**user_dict, **profile_dict}
        d = {}
        for i in info:
            if i in ['first_name', 'last_name', 'email', 'partner_email', 'partner_name']:
                d[i] = info[i]

        kwargs['initial'] = d
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Account'
        context['archive'] = Content.objects.filter(user=self.request.user).order_by('-time_create')[:5]
        context['paypal'] = os.getenv('PAYPAL_KEY')
        context['SCRIPT'] = ScriptsHead.objects.first()

        context['url_copy'] = f'{self.request.build_absolute_uri(reverse("register"))}?referral={self.request.user.profile.referral_code}'

        d = CreditsBuyPriceAndCount.objects.last()
        context['credits_buy'] = d if d else {'credits_count': 50, 'price': 2.00}

        return context

    def form_valid(self, form):
        data = form.cleaned_data
        self.request.user.first_name = data.get('first_name')
        self.request.user.last_name = data.get('last_name')
        self.request.user.email = data.get('email')
        self.request.user.save()

        self.request.user.profile.partner_email = data.get('partner_email')
        self.request.user.profile.partner_name = data.get('partner_name')
        self.request.user.profile.save()

        return super().form_valid(form)


class ChangePasswordView(FormView):
    template_name = 'generate/change_password.html'
    form_class = ChangePasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Change Password'
        context['SCRIPT'] = ScriptsHead.objects.first()
        return context

    def get_form_kwargs(self):
        kwargs = super(ChangePasswordView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse_lazy('account')


# FORGOT PASSWORD
class ChangePasswordReset(PasswordResetView):
    template_name = 'generate/reset_password.html'
    form_class = ResetPasswordEmail

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['SCRIPT'] = ScriptsHead.objects.first()
        return context


class ChangePasswordResetDone(PasswordResetDoneView):
    template_name = 'generate/reset_password_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['SCRIPT'] = ScriptsHead.objects.first()
        return context


class ChangePasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'generate/reset_password_confirm.html'
    form_class = SetPassword

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['SCRIPT'] = ScriptsHead.objects.first()
        return context


class ChangePasswordResetComplete(PasswordResetCompleteView):
    template_name = 'generate/reset_password_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['SCRIPT'] = ScriptsHead.objects.first()
        return context


class ContactView(FormView):
    template_name = 'generate/contact.html'
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['SCRIPT'] = ScriptsHead.objects.first()
        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = f'{form.cleaned_data["message"]}\n\nUser: {form.cleaned_data["first_name"]} {form.cleaned_data["last_name"]} \n\nEMAIL from : {form.cleaned_data["email"]}'

            SendAdminEmail(subject, message).start()

            messages.success(request, 'Your email has been sent to the site administrator. Thanks for the feedback')

        return redirect(request.path)


# sends
def send_to_my_email(request, content_id):
    if request.user.is_authenticated:
        content = Content.objects.get(id=content_id)
        if request.user != content.user:
            messages.error(request, "You can't send this content")
            return redirect('generate')
    else:
        return redirect('login')

    SendMyEmails(content.title, content.text.replace('\n', '<br>'), [content.user.email]).start()
    messages.success(request, "Your letter has been sent to your mail")

    return redirect('content', content_id=content_id)


def send_to_partner_email(request, content_id):
    if request.user.is_authenticated:
        content = Content.objects.get(id=content_id)
        if request.user != content.user:
            messages.error(request, "You can't send this content")
            return redirect('generate')

        if not request.user.profile.partner_email:
            messages.info(request, "Please enter your partner's email")
            return redirect('account')
    else:
        return redirect('login')

    SendMyEmails(content.title, content.text.replace('\n', '<br>'), [content.user.profile.partner_email]).start()
    messages.success(request, "Your letter has been sent to your partner's email")

    return redirect('content', content_id=content_id)
