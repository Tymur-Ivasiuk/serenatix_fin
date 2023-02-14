from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, SetPasswordForm, \
    PasswordResetForm
from phonenumber_field.formfields import PhoneNumberField

from generate.models import User


class LoginUserForm(AuthenticationForm):
    username = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'auth-input', 'placeholder': 'Email Address'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Enter Password'})
    )


class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'auth-input', 'placeholder': 'Email Address'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Create Password'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')


class GenerateForm(forms.Form):
    content_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'select_input-hidden', 'placeholder': 'Content type'})
    )
    relationship_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'select_input-hidden', 'placeholder': 'Relationship type'})
    )
    partner_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'generate-input', 'placeholder': 'Partner name'})
    )
    relationship_start_date = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={"min": "1920"})
    )
    occasion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'select_input-hidden', 'placeholder': 'Occasion'})
    )
    style = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'select_input-hidden', 'placeholder': 'Style'})
    )
    tone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'select_input-hidden', 'placeholder': 'Tone'})
    )
    genders = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'select_input-hidden', 'placeholder': 'Gender'})
    )


class AccountForm(forms.Form):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'generate-input', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'generate-input', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'generate-input', 'placeholder': 'Email Address'})
    )

    #partner
    partner_email = forms.CharField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'generate-input', 'placeholder': 'Partner email'})
    )
    partner_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'generate-input', 'placeholder': 'Partner name'})
    )


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'generate-input'})
    )
    new_password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'generate-input'})
    )
    new_password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'generate-input'})
    )


#FORGOT PASSWORD
class ResetPasswordEmail(PasswordResetForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'generate-input', 'placeholder': 'Your email'})
    )

class SetPassword(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'generate-input', 'placeholder': 'New password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'generate-input', 'placeholder': 'Confirm password'}),
    )


class ContactForm(forms.Form):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'generate-input', 'placeholder': 'First name *'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'generate-input', 'placeholder': 'Last name *'})
    )
    subject = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'generate-input', 'placeholder': 'Subject *'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'generate-input', 'placeholder': 'Email *'})
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Message'})
    )
