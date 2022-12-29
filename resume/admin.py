from django.contrib import admin
from .models import *


admin.site.register(Positions)
admin.site.register(EntityFavorite)
admin.site.register(CVView)


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('specialization',)}


class PhoneInline(admin.TabularInline):
    model = ResumePhone
    max_num = 10
    extra = 1


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    max_num = 10
    extra = 1


class EducationInline(admin.TabularInline):
    model = Education
    max_num = 1


class CourseInline(admin.TabularInline):
    model = Course
    max_num = 10
    extra = 1


class LanguageInline(admin.TabularInline):
    model = Language
    max_num = 10
    extra = 1


class PortfolioInline(admin.TabularInline):
    model = Portfolio
    max_num = 10
    extra = 1


class RecommendationInline(admin.TabularInline):
    model = Recommendation
    max_num = 10
    extra = 1


class ResumeCommentInline(admin.TabularInline):
    model = ResumeComment
    max_num = 10
    extra = 1


@admin.register(Resume)
class AboutAdmin(admin.ModelAdmin):
    inlines = [PhoneInline, WorkExperienceInline, EducationInline, CourseInline, LanguageInline,
               PortfolioInline, RecommendationInline, ResumeCommentInline]
    readonly_fields = ('created_at', 'up_time')
    search_fields = ('position',)







