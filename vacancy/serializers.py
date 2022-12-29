from rest_framework import serializers

from accounts.models import EntityProfile, EntityPersonal
from accounts.utils import send_postings
from resume.models import Positions, ResumePhone, Specialization

from vacancy.models import Vacancy, Postings, VacancyComment


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityProfile
        fields = ['company', 'address', 'image', 'id']


class AdminPageProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityProfile
        fields = ['company', 'address', 'image', 'id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['username'] = instance.user.username

        return representation


class EntityPersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityPersonal
        fields = ('id', 'email', 'full_name', 'position', 'phone',)


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = '__all__'


class MeVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if EntityProfile.objects.filter(user=instance.user):
            representation['profile'] = AdminPageProfileSerializer(EntityProfile.objects.get(user=instance.user),
                                                          context=self.context).data
        if EntityPersonal.objects.filter(id=representation.get('personal')):
            representation['personal'] = EntityPersonalSerializer(
                EntityPersonal.objects.get(id=representation.get('personal')), context=self.context).data

        representation['postings'] = PostingsSerializer(instance.postings.all(),
                                                        many=True, context=self.context).data
        representation['comments'] = VacancyCommentSerializer(instance.comments.all(),
                                                              many=True, context=self.context).data
        categories = []
        for c in instance.specialization.all():
            categories.append({c.slug: c.specialization})
        representation['specs'] = categories

        return representation


class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if EntityProfile.objects.filter(user=instance.user):
            representation['profile'] = ProfileSerializer(EntityProfile.objects.get(user=instance.user),
                                                          context=self.context).data
        if EntityPersonal.objects.filter(id=representation.get('personal')):
            representation['personal'] = EntityPersonalSerializer(
                EntityPersonal.objects.get(id=representation.get('personal')), context=self.context).data

        representation['comments'] = VacancyCommentSerializer(instance.comments.all(),
                                                              many=True, context=self.context).data
        categories = []
        for c in instance.specialization.all():
            categories.append({c.slug: c.specialization})
        representation['specs'] = categories

        return representation

    def create(self, validated_data):
        specializations = validated_data.pop('specialization')
        vacancy = Vacancy.objects.create(**validated_data)
        vacancy.is_moderation = False
        vacancy.save()
        if specializations:
            for s in specializations:
                if s.parent_specialization:
                    specializations.append(s.parent_specialization)
            vacancy.specialization.add(*specializations)

        comments = validated_data.get('comments')
        if comments:
            VacancyComment.objects.bulk_create([VacancyComment(vacancy=vacancy, **com) for com in comments])

        return vacancy

    def update(self, instance, validated_data):
        request = self.context.get('request')
        vacancy = instance
        specializations = validated_data.pop('specialization')
        vip_rubrics = validated_data.pop('vip_rubrics')

        for key, value in validated_data.items():
            setattr(instance, key, value)

        for k, v in validated_data.items():
            vacancy.k = v
            vacancy.save()

        if request.user.user_status == 'entity':
            vacancy.is_moderation = False
            vacancy.is_active = False
        vacancy.save()

        if vacancy.is_moderation is True:
            if not Positions.objects.filter(title=validated_data.get('position')):
                Positions.objects.create(title=validated_data.get('position'))

        if specializations:
            vacancy.specialization.clear()
            for s in specializations:
                if s.parent_specialization:
                    specializations.append(s.parent_specialization)
            instance.specialization.add(*specializations)

        if vip_rubrics:
            instance.vip_rubrics.clear()
            instance.vip_rubrics.add(*vip_rubrics)

        comments = validated_data.get('comments')
        if comments:
            VacancyComment.objects.filter(vacancy=vacancy).delete()
            VacancyComment.objects.bulk_create([VacancyComment(vacancy=vacancy, **com) for com in comments])

        return vacancy


class VacancyCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyComment
        fields = ('manager', 'text', 'created_at')


class PostingsVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ('position',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['profile'] = ProfileSerializer(instance.user.entity_profile).data
        return representation


class PostingsResumePhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumePhone
        fields = ('phone', )


class PostingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Postings
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['info'] = PostingsVacancySerializer(instance.vacancy).data
        representation['resume_phone'] = PostingsResumePhoneSerializer(instance.resume.phones.all(), many=True).data
        representation['resume_email'] = instance.resume.user.email
        representation['resume_social_media_type'] = instance.resume.social_media_type
        representation['resume_social_media_text'] = instance.resume.social_media_text

        return representation

    # def update(self, instance, validated_data):
    #     if validated_data.is_invited is True:
    #         for key, value in validated_data.items():
    #             setattr(instance, key, value)
    #
    #         email = validated_data.resume.user.email
    #         text = 'Вы получили приглашение '
    #         send_postings(email=email, text=text)
    #
    #     return instance



