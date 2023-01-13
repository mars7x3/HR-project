
from rest_framework import serializers

from accounts.models import EntityProfile
from vacancy.models import Postings
from vacancy.serializers import PostingsSerializer
from .models import *
from .utils import parse_val


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['count_v'] = len(instance.spec_vacancies.filter(vip_status=False, is_active=True, archive=False))
        representation['count_r'] = len(instance.spec_resumes.filter(vip_status=False, is_active=True, status_is_hidden=False))
        return representation


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['recommendations'] = RecommendationSerializer(instance.recommendations.all(),
                                                                     many=True, context=self.context).data
        representation['portfolios'] = PortfolioSerializer(instance.portfolios.all(),
                                                           many=True, context=self.context).data
        representation['languages'] = LanguageSerializer(instance.languages.all(),
                                                        many=True, context=self.context).data
        representation['courses'] = CourseSerializer(instance.courses.all(),
                                                    many=True, context=self.context).data
        representation['educations'] = EducationSerializer(instance.educations.all(),
                                                          many=True, context=self.context).data
        representation['experiences'] = WorkExperienceSerializer(instance.experiences.all(),
                                                                many=True, context=self.context).data
        representation['comments'] = ResumeCommentSerializer(instance.comments.all(),
                                                             many=True, context=self.context).data
        categories = []
        for c in instance.specialization.all():
            categories.append({c.slug: c.specialization})
        representation['specs'] = categories

        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        try: specializations = validated_data.pop('specialization')
        except: specializations = None
        resume = Resume.objects.create(**validated_data)
        resume.is_moderation = False
        resume.save()

        if specializations:
            for s in specializations:
                if s.parent_specialization:
                    specializations.append(s.parent_specialization)
            resume.specialization.add(*specializations)

        recommendations = request.data.get('recommendations')
        if recommendations:
            recommendations = parse_val(recommendations)
            Recommendation.objects.bulk_create([Recommendation(resume=resume, **rec) for rec in recommendations])

        portfolios = request.data.get('portfolios')
        if portfolios:
            portfolios = parse_val(portfolios)
            Portfolio.objects.bulk_create([Portfolio(resume=resume, **por) for por in portfolios])

        languages = request.data.get('languages')
        if languages:
            languages = parse_val(languages)
            Language.objects.bulk_create([Language(resume=resume, **lan) for lan in languages])

        courses = request.data.get('courses')
        if courses:
            courses = parse_val(courses)
            Course.objects.bulk_create([Course(resume=resume, **cou) for cou in courses])

        educations = request.data.get('educations')
        if educations:
            educations = parse_val(educations)
            Education.objects.bulk_create([Education(resume=resume, **edu) for edu in educations])

        experiences = request.data.get('experiences')
        if experiences:
            experiences = parse_val(experiences)
            WorkExperience.objects.bulk_create([WorkExperience(resume=resume, **exp) for exp in experiences])

        phones = request.data.get('phones')
        if phones:
            phones = parse_val(phones)
            ResumePhone.objects.bulk_create([ResumePhone(resume=resume, **pho) for pho in phones])

        comments = request.data.get('comments')
        if comments:
            comments = parse_val(comments)
            ResumeComment.objects.bulk_create([ResumeComment(resume=resume, **com) for com in comments])

        return resume

    def update(self, instance, validated_data):
        request = self.context.get('request')
        resume = instance

        try: specializations = validated_data.pop('specialization')
        except: specializations = None
        for key, value in validated_data.items():
            setattr(resume, key, value)
        for k, v in validated_data.items():
            resume.k = v
            resume.save()

        if specializations:
            resume.specialization.clear()
            for s in specializations:
                if s.parent_specialization:
                    specializations.append(s.parent_specialization)
            resume.specialization.add(*specializations)

        if request.user.user_status == 'applicant':
            resume.is_moderation = False
            resume.is_active = False

        resume.save()

        recommendations = request.data.get('recommendations')

        if recommendations:
            Recommendation.objects.filter(resume=resume).delete()
            recommendations = parse_val(recommendations)
            Recommendation.objects.bulk_create([Recommendation(resume=resume, **rec) for rec in recommendations])

        portfolios = request.data.get('portfolios')
        if portfolios:
            Portfolio.objects.filter(resume=resume).delete()
            portfolios = parse_val(portfolios)
            Portfolio.objects.bulk_create([Portfolio(resume=resume, **por) for por in portfolios])

        languages = request.data.get('languages')
        if languages:
            Language.objects.filter(resume=resume).delete()
            languages = parse_val(languages)
            Language.objects.bulk_create([Language(resume=resume, **lan) for lan in languages])

        courses = request.data.get('courses')
        if courses:
            Course.objects.filter(resume=resume).delete()
            courses = parse_val(courses)
            Course.objects.bulk_create([Course(resume=resume, **cou) for cou in courses])

        educations = request.data.get('educations')
        if educations:
            Education.objects.filter(resume=resume).delete()
            educations = parse_val(educations)
            Education.objects.bulk_create([Education(resume=resume, **edu) for edu in educations])

        experiences = request.data.get('experiences')
        if experiences:
            WorkExperience.objects.filter(resume=resume).delete()
            experiences = parse_val(experiences)
            WorkExperience.objects.bulk_create([WorkExperience(resume=resume, **exp) for exp in experiences])

        phones = request.data.get('phones')
        if phones:
            ResumePhone.objects.filter(resume=resume).delete()
            phones = parse_val(phones)
            ResumePhone.objects.bulk_create([ResumePhone(resume=resume, **pho) for pho in phones])

        comments = request.data.get('comments')
        if comments:
            ResumeComment.objects.filter(resume=resume).delete()
            comments = parse_val(comments)
            ResumeComment.objects.bulk_create([ResumeComment(resume=resume, **com) for com in comments])

        return resume


class MeInfoResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['recommendations'] = RecommendationSerializer(instance.recommendations.all(),
                                                                    many=True, context=self.context).data
        representation['portfolios'] = PortfolioSerializer(instance.portfolios.all(),
                                                          many=True, context=self.context).data
        representation['languages'] = LanguageSerializer(instance.languages.all(),
                                                        many=True, context=self.context).data
        representation['courses'] = CourseSerializer(instance.courses.all(),
                                                    many=True, context=self.context).data
        representation['educations'] = EducationSerializer(instance.educations.all(),
                                                          many=True, context=self.context).data
        representation['experiences'] = WorkExperienceSerializer(instance.experiences.all(),
                                                                many=True, context=self.context).data
        representation['postings'] = PostingsSerializer(instance.postings.all(),
                                                        many=True, context=self.context).data
        representation['comments'] = ResumeCommentSerializer(instance.comments.all(),
                                                             many=True, context=self.context).data
        representation['phones'] = PhoneSerializer(instance.phones.all(),
                                                         many=True, context=self.context).data
        representation['postings'] = PostingsSerializer(instance.postings.all(), many=True, context=self.context).data
        representation['cvviews'] = CVViewSerializer(instance.cvviews.all(), many=True, context=self.context).data
        categories = []
        for c in instance.specialization.all():
            categories.append({c.slug: c.specialization})
        representation['specs'] = categories
        return representation


class ResumeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeComment
        fields = ('manager', 'text', 'created_at')


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ('place_of_work', 'full_name', 'position', 'email', 'phone')


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ('title', 'file', 'link')


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ('title', 'level')


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('company', 'title', 'date_finish', 'description')


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ('category', 'institution', 'faculty', 'date_finish')


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ('place_of_work', 'position', 'field_of_activity', 'city', 'work_date_from', 'work_date_to',
                  'description')


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumePhone
        fields = ('phone',)


class ResumePhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ('id', )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['phones'] = PhoneSerializer(instance.phones.all(), many=True, context=self.context).data
        representation['email'] = instance.user.email
        representation['instagram'] = instance.instagram
        representation['social_type'] = instance.social_media_type
        representation['social_text'] = instance.social_media_text

        return representation


class PositionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Positions
        fields = '__all__'


class CVViewEntityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityProfile
        fields = ('company',)


class CVViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVView
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['info'] = CVViewEntityProfileSerializer(instance.company.entity_profile).data

        return representation



