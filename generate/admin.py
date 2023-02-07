from django.contrib import admin
from adminsortable2.admin import SortableAdminBase, SortableTabularInline, SortableAdminMixin

from .models import *


class AnswersInlines(SortableTabularInline, admin.TabularInline):
    model = Answers
    extra = 0


class QuestionsAdmin(SortableAdminBase, admin.ModelAdmin):
    search_fields = ['title']
    list_per_page = 20

    inlines = [
        AnswersInlines
    ]


@admin.register(PoemStyles)
class PoemStylesAdmin(admin.ModelAdmin):
    fields = ['title']
    list_display = ['title']


@admin.register(LetterStyles)
class LetterStylesAdmin(admin.ModelAdmin):
    fields = ['title']
    list_display = ['title']


@admin.register(Length)
class LengthAdmin(admin.ModelAdmin):
    fields = ['title']
    list_display = ['title']


@admin.register(Tone)
class ToneAdmin(admin.ModelAdmin):
    fields = ['title']
    list_display = ['title']


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    fields = ['title']
    list_display = ['title']


class RelationshipTypesAdmin(admin.ModelAdmin):
    fields = ['title']
    list_display = ['title']


admin.site.register(Profile)
admin.site.register(Content)
admin.site.register(Questions, QuestionsAdmin)
admin.site.register(CreditsPrice)
admin.site.register(RelationshipTypes, RelationshipTypesAdmin)
admin.site.register(CreditsBuyPriceAndCount)
admin.site.register(Transactions)
