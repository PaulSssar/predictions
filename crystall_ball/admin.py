from django.contrib import admin
from django.utils.html import format_html

from crystall_ball.models import Answer, Question, Cards

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'text_preview')
    readonly_fields = ('text',)

    def text_preview(self, obj):
        return obj.text[:100]
    text_preview.short_description = 'Текст (превью)'


class AnswerInline(admin.TabularInline):
    model = Answer

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline, ]

@admin.register(Cards)
class CardsAdmin(admin.ModelAdmin):
    readonly_fields = [
        'image_card_preview'
    ]
    fields = [
        'name',
        'position',
        'number_of_card',
        'image',
        'image_card_preview',
    ]
    list_display = (
        'name',
        'position',
        'number_of_card',
        'image_card_preview'
    )

    def image_card_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="300" />', obj.image.url)
        return 'No image'