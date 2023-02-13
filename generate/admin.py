from django.contrib import admin
from adminsortable2.admin import SortableAdminBase, SortableTabularInline, SortableAdminMixin
from import_export.admin import ExportActionMixin

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


class ContentAdmin(ExportActionMixin, admin.ModelAdmin):
    actions = ["export_as_csv"]




class StylesInlines(SortableTabularInline, admin.TabularInline):
    model = ContentStyles
    extra = 0

class ContentTypesAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = [
        StylesInlines,
    ]

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Content, ContentAdmin)
admin.site.register(Questions, QuestionsAdmin)
admin.site.register(ContentTypes, ContentTypesAdmin)
admin.site.register(RelationshipTypes, RelationshipTypesAdmin)
admin.site.register(CreditsBuyPriceAndCount)
admin.site.register(Transactions)
admin.site.register(ScriptsHead)
