from ckeditor.fields import RichTextField
from django.db import models

from accounts.models import MyUser, EntityPersonal, Manager
from resume.models import Specialization, Resume


class Vacancy(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='vacancies')
    personal = models.ForeignKey(EntityPersonal, on_delete=models.SET_NULL, blank=True, null=True,
                                 related_name='personal_vacancies')
    specialization = models.ManyToManyField(Specialization, related_name='spec_vacancies')
    position = models.CharField(max_length=300)
    salary = models.IntegerField(default=0)
    negotiable = models.BooleanField(default=False)
    experience = models.CharField(max_length=20, blank=True)
    schedule = models.CharField(max_length=100)
    education = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    group = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    up_time = models.DateTimeField(auto_now=True)
    requirements = RichTextField()
    terms = RichTextField()
    responsibilities = RichTextField()
    appeal = RichTextField()
    vip_status = models.BooleanField(default=False)
    vip_rubrics = models.ManyToManyField(Specialization, blank=True, related_name='vip_rubrics_vacancies')
    up_status_10 = models.BooleanField(default=False)
    vip_dead_time = models.DateTimeField(blank=True, null=True)
    archive = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    moderation_comment = models.TextField(blank=True)
    is_moderation = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}. {self.user.email} - {self.position}"

    class Meta:
        ordering = ('-up_time',)




class Postings(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='postings')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='postings')
    applicant_is_viewed = models.BooleanField(default=False)
    is_viewed = models.BooleanField(default=False)
    is_invited = models.BooleanField(default=False)
    is_denied = models.BooleanField(default=False)
    text = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.resume.user.email} - {self.resume.position} || {self.vacancy}"

    class Meta:
        ordering = ('-created_at',)


class ApplicantFavorite(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='favorite_vacancies')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    favorite = models.BooleanField(default=False)


class VacancyComment(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='comments')
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, blank=True, null=True, related_name='vacancy_comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


