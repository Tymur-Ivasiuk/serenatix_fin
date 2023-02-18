from django.contrib import admin
from adminsortable2.admin import SortableAdminBase, SortableTabularInline, SortableAdminMixin
from import_export.admin import ExportActionMixin

from .models import *


class AnswersInlines(SortableTabularInline, admin.TabularInline):
    model = Answers
    extra = 0


class QuestionsAdmin(SortableAdminMixin, SortableAdminBase, admin.ModelAdmin):
    search_fields = ['question']

    list_display = ['question', 'content_type', 'is_publish', 'my_order']
    ordering = ['my_order']

    inlines = [
        AnswersInlines
    ]



@admin.register(Length)
class LengthAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'my_order']
    ordering = ['my_order']


@admin.register(Tone)
class ToneAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'my_order']
    ordering = ['my_order']


@admin.register(Occasion)
class OccasionAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'my_order']
    ordering = ['my_order']


class RelationshipTypesAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'my_order']
    ordering = ['my_order']


class ContentAdmin(ExportActionMixin, admin.ModelAdmin):
    actions = ["export_as_csv"]
    list_display = ['title', 'content_type', 'user']
    list_filter = ['content_type']


class StylesInlines(SortableTabularInline, admin.TabularInline):
    model = ContentStyles
    extra = 0

class ContentTypesAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ['title', 'credits']

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
admin.site.register(PromptText)
admin.site.register(Banners)
