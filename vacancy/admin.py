from django.contrib import admin

from vacancy.models import *

admin.site.register(Postings)
admin.site.register(ApplicantFavorite)


class VacancyCommentInline(admin.TabularInline):
    model = VacancyComment
    max_num = 10
    extra = 1


@admin.register(Vacancy)
class AboutAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'up_time')
    inlines = [VacancyCommentInline]
    search_fields = ('position',)

