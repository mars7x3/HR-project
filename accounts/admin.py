from django.contrib import admin

from accounts.models import *


class MyUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username')
    list_display_links = ('id', 'email', 'username')
    search_fields = ('username', 'email')


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(EmailAndCode)
admin.site.register(Manager)
admin.site.register(EntityPersonal)
admin.site.register(ProfileComment)
admin.site.register(PasswordTest)


class ProfilePhoneInline(admin.TabularInline):
    model = EntityProfilePhone
    max_num = 5
    extra = 1


class EntityPersonalInline(admin.TabularInline):
    model = EntityPersonal
    max_num = 20
    extra = 1


class DocumentInline(admin.TabularInline):
    model = Document
    max_num = 20
    extra = 1


class EntityRequisiteInline(admin.TabularInline):
    model = EntityRequisite
    max_num = 20
    extra = 1


class ProfileCommentInline(admin.TabularInline):
    model = ProfileComment
    max_num = 10
    extra = 1


@admin.register(EntityProfile)
class EntityProfileAdmin(admin.ModelAdmin):
    inlines = [ProfilePhoneInline, EntityRequisiteInline, EntityPersonalInline, DocumentInline, ProfileCommentInline]

