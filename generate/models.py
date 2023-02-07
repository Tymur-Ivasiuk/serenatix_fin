from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField


from generate.validators import validate_positive



def get_user_email(self):
    return self.email
User.add_to_class("__str__", get_user_email)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credits_count = models.PositiveIntegerField(default=0)
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    partner_email = models.EmailField(null=True, blank=True)
    partner_phone_number = PhoneNumberField(null=True, blank=True)

    not_anonim = models.BooleanField(default=False)

    save_answers = models.JSONField(null=True)

    def __str__(self):
        return self.user.email

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        instance.username = instance.email.split('@')[0]
        instance.save()
        Profile.objects.create(user=instance)
    else:
        try:
            instance.profile.save()
        except:
            pass


class Content(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    types = [
        ('letter', 'letter'),
        ('poem', 'poem'),
        ('note', 'note'),
    ]
    content_type = models.CharField(max_length=50, choices=types)

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

    def __str__(self):
        return self.question


class Answers(models.Model):
    answer = models.CharField(max_length=255)
    question = models.ForeignKey('Questions', on_delete=models.CASCADE)

    my_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, db_index=True)

    def __str__(self):
        return self.answer

    class Meta:
        ordering = ['my_order']


class PoemStyles(models.Model):
    title = models.CharField(max_length=100)

    my_order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['my_order']


class LetterStyles(models.Model):
    title = models.CharField(max_length=100)

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


class CreditsPrice(models.Model):
    credits = models.PositiveIntegerField(default=1)

    types = [
        ('letter', 'letter'),
        ('poem', 'poem'),
        ('note', 'note'),
    ]
    credits_type = models.CharField(max_length=50, choices=types)

    def __str__(self):
        return self.credits_type


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

