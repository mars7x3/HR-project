from django.db import models

from accounts.models import MyUser, Manager


class Specialization(models.Model):
    specialization = models.CharField(max_length=100)
    slug = models.CharField(unique=True, primary_key=True, max_length=100)
    parent_specialization = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                              related_name='parent_spec')

    def __str__(self):
        if self.parent_specialization:
            return f'{self.parent_specialization} - {self.specialization}'
        return self.specialization


class Resume(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='resume')
    image = models.FileField(upload_to='resume-images', blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    agge = models.DateField(max_length=20)
    gender = models.CharField(max_length=10)
    current_city = models.CharField(max_length=50)
    social_media_type = models.CharField(max_length=50, blank=True)
    social_media_text = models.CharField(max_length=100, blank=True)
    family_position = models.BooleanField(default=False)
    having_children = models.BooleanField(default=False)
    business_trips = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=300)
    specialization = models.ManyToManyField(Specialization, related_name='spec_resumes')
    salary = models.IntegerField(default=0)
    negotiable = models.BooleanField(default=False)
    city_for_work = models.CharField(max_length=20, blank=True)
    type_of_employment = models.CharField(max_length=50)
    additional_information = models.TextField(blank=True)
    no_experience = models.BooleanField(default=False)
    auto = models.BooleanField(default=False)
    driver_license = models.CharField(max_length=100, blank=True)
    key_skills = models.TextField(blank=True)
    pk_lvl = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    up_time = models.DateTimeField(auto_now=True)
    vip_status = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    moderation_comment = models.TextField(blank=True, null=True)
    is_moderation = models.BooleanField(default=False)
    instagram = models.CharField(max_length=200, blank=True)
    status_is_view_all = models.BooleanField(default=False)
    status_is_hidden = models.BooleanField(default=False)
    status_active_search = models.BooleanField(default=False)
    status_variant_view = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.id}. {self.user.email} - {self.last_name} {self.name}'

    class Meta:
        ordering = ('-up_time',)


class Recommendation(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='recommendations')
    place_of_work = models.CharField(max_length=350, null=True)
    full_name = models.CharField(max_length=200, null=True)
    position = models.CharField(max_length=300, null=True)
    email = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=20, null=True)


class Portfolio(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='portfolios')
    title = models.CharField(max_length=300, null=True)
    file = models.FileField(upload_to='portfolio-images', null=True)
    link = models.CharField(max_length=500, null=True)


class Language(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='languages')
    title = models.CharField(max_length=30, null=True)
    level = models.CharField(max_length=30, null=True)


class Course(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='courses')
    company = models.CharField(max_length=250, null=True)
    title = models.CharField(max_length=250, null=True)
    date_finish = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)


class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='educations')
    category = models.CharField(max_length=100)
    institution = models.CharField(max_length=250)
    faculty = models.CharField(max_length=250)
    date_finish = models.CharField(max_length=100)


class WorkExperience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    place_of_work = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    field_of_activity = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    work_date_from = models.CharField(max_length=100)
    work_date_to = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        ordering = ('id',)


class ResumePhone(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='phones')
    phone = models.CharField(max_length=20)


class Positions(models.Model):
    title = models.CharField(max_length=300, verbose_name='Название позиции')

    def __str__(self):
        return self.title


class EntityFavorite(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='favorite_resumes')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='resume_favorite')
    favorite = models.BooleanField(default=False)


class ResumeComment(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='comments')
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, blank=True, null=True, related_name='resume_comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class CVView(models.Model):
    # просмотр резюме от компании
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='cvviews')
    company = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='cvviews')
    is_viewed = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resume} - {self.company.username}"


