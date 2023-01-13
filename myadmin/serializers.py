from rest_framework import serializers

from accounts.models import EntityProfile
from resume.models import Resume, Recommendation, Portfolio, Language, Course, Education, WorkExperience, ResumePhone, \
    ResumeComment
from resume.serializers import RecommendationSerializer, PortfolioSerializer, LanguageSerializer, CourseSerializer, \
    EducationSerializer, WorkExperienceSerializer, ResumeCommentSerializer, ResumePhoneSerializer, PhoneSerializer
from tariffs.models import UserTariffFunction

from vacancy.serializers import PostingsSerializer, ProfileSerializer
from .models import *


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['percent'] = round(instance.done / (instance.amount / 100))
        representation['manager'] = instance.manager.manager.username
        representation['manager_id'] = instance.manager.id
        representation['manager_name'] = instance.manager.manager_name

        return representation


class PayHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayHistory
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for p in EntityProfile.objects.filter(company=instance.company):
            if p.user.username == instance.wallet:
                representation['profile_id'] = p.id

        return representation


class TermsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsHistory
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['company'] = instance.company.entity_profile.company
        representation['company_id'] = instance.company.id
        representation['manager'] = instance.manager.manager.username
        representation['manager_id'] = instance.manager.id
        representation['profile_id'] = instance.company.entity_profile.id

        return representation


class LimitsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LimitsHistory
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['company'] = instance.company.entity_profile.company
        representation['company_id'] = instance.company.id
        representation['manager'] = instance.manager.manager.username
        representation['manager_id'] = instance.manager.id
        representation['profile_id'] = instance.company.entity_profile.id

        return representation


class DumpsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DumpsHistory
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['company'] = instance.company.entity_profile.company
        representation['company_id'] = instance.company.id
        representation['manager'] = instance.manager.manager.username
        representation['manager_id'] = instance.manager.id
        representation['profile_id'] = instance.company.entity_profile.id

        return representation


class DebtorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debtors
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['company'] = instance.company.entity_profile.company
        representation['company_id'] = instance.company.id
        representation['manager'] = instance.manager.manager.username
        representation['manager_id'] = instance.manager.id
        representation['profile_id'] = instance.company.entity_profile.id

        return representation


class AdminResumeSerializer(serializers.ModelSerializer):
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
        categories = []
        for c in instance.specialization.all():
            categories.append({c.slug: c.specialization})
        representation['specs'] = categories

        return representation

    def update(self, instance, validated_data):
        request = self.context.get('request')
        resume = instance

        specializations = validated_data.pop('specialization')
        for key, value in validated_data.items():
            setattr(resume, key, value)
        for k, v in validated_data.items():
            resume.k = v
            resume.save()
        if specializations:
            resume.specialization.clear()
            resume.specialization.add(*specializations)

        recommendations = request.data.get('recommendations')

        if recommendations:
            Recommendation.objects.filter(resume=resume).delete()
            Recommendation.objects.bulk_create([Recommendation(resume=resume, **rec) for rec in recommendations])

        portfolios = request.data.get('portfolios')
        if portfolios:
            Portfolio.objects.filter(resume=resume).delete()
            Portfolio.objects.bulk_create([Portfolio(resume=resume, **por) for por in portfolios])

        languages = request.data.get('languages')
        if languages:
            Language.objects.filter(resume=resume).delete()
            Language.objects.bulk_create([Language(resume=resume, **lan) for lan in languages])

        courses = request.data.get('courses')
        if courses:
            Course.objects.filter(resume=resume).delete()
            Course.objects.bulk_create([Course(resume=resume, **cou) for cou in courses])

        educations = request.data.get('educations')
        if educations:
            Education.objects.filter(resume=resume).delete()
            Education.objects.bulk_create([Education(resume=resume, **edu) for edu in educations])

        experiences = request.data.get('experiences')
        if experiences:
            WorkExperience.objects.filter(resume=resume).delete()
            WorkExperience.objects.bulk_create([WorkExperience(resume=resume, **exp) for exp in experiences])

        phones = request.data.get('phones')
        if phones:
            ResumePhone.objects.filter(resume=resume).delete()

            ResumePhone.objects.bulk_create([ResumePhone(resume=resume, **pho) for pho in phones])

        comments = request.data.get('comments')
        if comments:
            ResumeComment.objects.filter(resume=resume).delete()
            ResumeComment.objects.bulk_create([ResumeComment(resume=resume, **com) for com in comments])

        return resume


class ManagerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'username')


class ManagerCustomListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ('id', 'manager_name', 'telegram', 'whatsapp', 'email')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['username'] = instance.manager.username
        representation['user'] = instance.manager.id

        return representation


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTariffFunction
        fields = ('user', 'id', 'banner', 'banner_moderation', 'banner_link', 'banner_image', 'banner_dead_time',
                  'banner_rubric_list', 'banner_is_active', 'banner_tariff_title')
        extra_kwargs = {
            'user': {'read_only': True},
            'banner': {'read_only': True},

        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if EntityProfile.objects.get(user=instance.user).company:
            representation['profile'] = ProfileSerializer(EntityProfile.objects.get(user=instance.user),
                                                          context=self.context).data

        return representation

    def update(self, instance, validated_data):
        tariff = instance
        try: banner_rubric_list = validated_data.pop('banner_rubric_list')
        except: pass

        for key, value in validated_data.items():
            setattr(tariff, key, value)
        for k, v in validated_data.items():
            tariff.k = v
            tariff.save()
        tariff.employer_moderation = True

        tariff.save()
        return tariff


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTariffFunction
        fields = ('user', 'id', 'employer', 'employer_moderation', 'employer_link', 'employer_image',
                  'employer_dead_time', 'employer_title', 'employer_is_active',
                  'employer_tariff_title')
        extra_kwargs = {
            'user': {'read_only': True},
            'employer': {'read_only': True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if EntityProfile.objects.get(user=instance.user).company:
            representation['profile'] = ProfileSerializer(EntityProfile.objects.get(user=instance.user),
                                                          context=self.context).data

        return representation

    def update(self, instance, validated_data):
        tariff = instance
        for key, value in validated_data.items():
            setattr(tariff, key, value)
        for k, v in validated_data.items():
            tariff.k = v
            tariff.save()
        tariff.employer_moderation = True

        tariff.save()
        return tariff


class EntityAllHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityAllHistory
        fields = "__all__"


class CallRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRequest
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['company'] = instance.company.entity_profile.company
        representation['manager'] = instance.manager.manager.username
        representation['profile_id'] = instance.company.entity_profile.id

        return representation


# class ActiveCodeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EmailAndCode
#         fields = "__all__"
