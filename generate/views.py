import json
import os

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
        context['title'] = 'Login'
        return context

    def form_valid(self, form):
        if not self.request.POST.get('remember', None):
            self.request.session.set_expiry(0)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'

        return context


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

        context['content_types'] = ['Letter', 'Poem', 'Note']
        context['poem_styles'] = PoemStyles.objects.all()
        context['letter_styles'] = LetterStyles.objects.all()
        context['tone'] = Tone.objects.all()
        context['occasion'] = Occasion.objects.all()
        context['relationship_types'] = RelationshipTypes.objects.all()

        context['url_copy'] = self.request.build_absolute_uri(reverse('welcome'))

        context['paypal'] = os.getenv('PAYPAL_KEY')

        d = CreditsBuyPriceAndCount.objects.last()
        context['credits_buy'] = d if d else {'credits_count': 50, 'price': 2.00}

        context['archive'] = Content.objects.filter(user=self.request.user).order_by('-time_create')[:5]

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if (request.POST.get('content_type') and request.POST.get('occasion') and request.POST.get('tone') and
                    request.POST.get('genders') and request.POST.get('relationship_type')):
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        d = {'Letter': 'letter', 'Poem': 'poem', 'Note': 'note'}

        if self.request.user.profile.credits_count < CreditsPrice.objects.filter(
                credits_type=d.get(self.request.POST.get('content_type'))).first().credits:
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

        context['questions'] = Questions.objects.all().prefetch_related('answers_set')
        context['saved_answers'] = self.request.user.profile.save_answers.get('answers', [])
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('save'):
            answers = []
            for i in dict(request.POST).items():
                try:
                    int(i[0])
                    answers += i[1]
                except:
                    pass
            request.user.profile.save_answers = {'answers': answers}
            request.user.profile.save()
            messages.success(request, 'Your checkbox answers have been saved')
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

        context['length'] = Length.objects.all()
        context['tones'] = Tone.objects.all()
        if context['content'].content_type == 'poem':
            context['styles'] = PoemStyles.objects.all()
        else:
            context['styles'] = LetterStyles.objects.all()

        context['answers_count'] = len(context['content'].answers.keys())
        context['questions_count'] = Questions.objects.all().count()

        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('length') or request.POST.get('styles') or request.POST.get('tones'):
            if self.request.user.profile.credits_count < CreditsPrice.objects.filter(
                    credits_type=request.POST.get('content_type')).first().credits:
                messages.error(request, "Sorry, you don't have enough credits")
                return redirect('generate')

            dict_info_content = Content.objects.get(id=self.kwargs.get('content_id')).content_info
            dict_info_content['length'] = request.POST.get('length')
            dict_info_content['tones'] = request.POST.get('tones')
            if dict_info_content.get('type') == 'Poem':
                dict_info_content['poem_style'] = request.POST.get('style')
            else:
                dict_info_content['letter_style'] = request.POST.get('style')
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
        context['ordering'] = {
            '-time_create': 'First new',
            'time_create': 'First old',
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

    if request.user.profile.credits_count < CreditsPrice.objects.filter(
            credits_type=content.content_type).first().credits:
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
            if i in ['first_name', 'last_name', 'email', 'phone_number', 'partner_email', 'partner_phone_number']:
                d[i] = info[i]

        kwargs['initial'] = d
        print(d)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Account'
        context['archive'] = Content.objects.filter(user=self.request.user).order_by('-time_create')[:5]
        context['paypal'] = os.getenv('PAYPAL_KEY')

        context['url_copy'] = self.request.build_absolute_uri(reverse('welcome'))

        d = CreditsBuyPriceAndCount.objects.last()
        context['credits_buy'] = d if d else {'credits_count': 50, 'price': 2.00}

        return context

    def form_valid(self, form):
        data = form.cleaned_data
        self.request.user.first_name = data.get('first_name')
        self.request.user.last_name = data.get('last_name')
        self.request.user.email = data.get('email')
        self.request.user.save()

        self.request.user.profile.phone_number = data.get('phone_number')
        self.request.user.profile.partner_email = data.get('partner_email')
        self.request.user.profile.partner_phone_number = data.get('partner_phone_number')
        self.request.user.profile.save()

        return super().form_valid(form)


class ChangePasswordView(FormView):
    template_name = 'generate/change_password.html'
    form_class = ChangePasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Change Password'

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


class ChangePasswordResetDone(PasswordResetDoneView):
    template_name = 'generate/reset_password_done.html'


class ChangePasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'generate/reset_password_confirm.html'
    form_class = SetPassword


class ChangePasswordResetComplete(PasswordResetCompleteView):
    template_name = 'generate/reset_password_complete.html'


class ContactView(FormView):
    template_name = 'generate/contact.html'
    form_class = ContactForm

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


def send_to_my_phone(request, content_id):
    if request.user.is_authenticated:
        content = Content.objects.get(id=content_id)
        if request.user != content.user:
            messages.error(request, "You can't send this content")
            return redirect('generate')

        if not request.user.profile.phone_number:
            messages.info(request, "Please enter your phone number")
            return redirect('account')
    else:
        return redirect('login')

    SmsThread(request.user.profile.phone_number, content.title, content.text).start()
    messages.success(request, "We have sent an SMS to your phone number")

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
