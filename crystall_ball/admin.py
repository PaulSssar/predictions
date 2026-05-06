from django.contrib import admin
from django.utils.html import format_html

from crystall_ball.models import Answer, Question, Cards

admin.site.register(Answer)
admin.site.register(Question)

@admin.register(Cards)
class ProfileAdmin(admin.ModelAdmin):
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
        'number_of_card'
    )

    def image_card_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="300" />', obj.image.url)
        return 'No image'