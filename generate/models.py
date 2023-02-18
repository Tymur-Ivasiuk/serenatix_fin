import os

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from generate.utils_models import generate_reff_code, generate_auth_token
from generate.validators import *

from dotenv import load_dotenv
load_dotenv()

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        '''Create and save a user with the given email, and
        password.
        '''
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must have is_staff=True.'
            )
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must have is_superuser=True.'
            )

        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        unique=True,
        max_length=255,
        blank=False,
    )

    # All these field declarations are copied as-is
    # from `AbstractUser`
    first_name = models.CharField(
        _('first name'),
        max_length=30,
        blank=True,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=True,
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into '
            'this admin site.'
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be '
            'treated as active. Unselect this instead '
            'of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )

    # Add additional fields here if needed

    def __str__(self):
        return str(self.email)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credits_count = models.PositiveIntegerField(default=0)
    partner_email = models.EmailField(null=True, blank=True)
    partner_name = models.CharField(max_length=255, null=True, blank=True)

    not_anonim = models.BooleanField(default=False)

    email_verify = models.BooleanField(default=False)
    email_code = models.CharField(max_length=50, blank=True)
    referral_code = models.CharField(max_length=12, blank=True)

    save_answers = models.JSONField(null=True, default={'answers': ''})

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = generate_reff_code()
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        instance.save()
        Profile.objects.create(user=instance, credits_count=os.environ.get('REGISTER_ADD_CREDITS', 0))
    else:
        try:
            instance.profile.save()
        except:
            pass


class ContentTypes(models.Model):
    title = models.CharField(max_length=255)
    credits = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class Content(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    content_type = models.ForeignKey('ContentTypes', on_delete=models.PROTECT)

    title = models.CharField(max_length=255)
    text = models.TextField()

    prompt = models.TextField()
    answers = models.JSONField()
    content_info = models.JSONField()

    time_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('content', kwargs={'content_id': self.id})


class Questions(models.Model):
    question = models.CharField(max_length=255)
    prompt_text = models.CharField(max_length=255)

    content_type = models.ForeignKey('ContentTypes', on_delete=models.PROTECT)

    is_publish = models.BooleanField(default=False)
    have_answers = models.BooleanField(default=True)

    my_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, db_index=True)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['my_order']

class Answers(models.Model):
    answer = models.CharField(max_length=255)
    question = models.ForeignKey('Questions', on_delete=models.CASCADE)

    my_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, db_index=True)

    def __str__(self):
        return self.answer

    class Meta:
        ordering = ['my_order']


class ContentStyles(models.Model):
    title = models.CharField(max_length=100)
    content_type = models.ForeignKey('ContentTypes', on_delete=models.CASCADE)
    my_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['my_order']


class Tone(models.Model):
    title = models.CharField(max_length=100)

    my_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['my_order']


class Length(models.Model):
    title = models.CharField(max_length=100)

    my_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['my_order']


class Occasion(models.Model):
    title = models.CharField(max_length=100)

    my_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['my_order']


class RelationshipTypes(models.Model):
    title = models.CharField(max_length=100)

    my_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['my_order']



class CreditsBuyPriceAndCount(models.Model):
    credits_count = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2, validators=[validate_positive])

    def __str__(self):
        return str(self.credits_count)


class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credits_count = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2, validators=[validate_positive])

    time_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.email)


class ScriptsHead(models.Model):
    script = models.TextField()

    def __str__(self):
        return self.script

class PromptText(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text


class Banners(models.Model):
    image = models.ImageField(upload_to="img/%Y/%m/%d")

    orientation_choice = [
        ('Horizontal', 'Horizontal'),
        ('Vertical', 'Vertical'),
    ]
    orientation = models.CharField(max_length=50, choices=orientation_choice)
