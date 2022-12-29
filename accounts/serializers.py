from uuid import uuid4

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from myadmin.serializers import EntityAllHistorySerializer
from resume.models import EntityFavorite
from resume.serializers import ResumeSerializer, MeInfoResumeSerializer
from test_wallet.models import Wallet
from test_wallet.serializers import WalletSerializer
from vacancy.models import Vacancy, ApplicantFavorite
from vacancy.serializers import VacancySerializer, MeVacancySerializer
from .models import *


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'email', 'user_status', 'username')

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     if instance.manager:
    #         rep['info'] = ManagerSerializer(instance.manager).data
    #
    #     return rep


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_status'] = self.user.user_status
        data['user'] = self.user.id
        return data


class AuthenticatedUserSerializer(serializers.ModelSerializer):
    class Meta:
        user_field = 'user'
        extra_kwargs = {
            user_field: {'read_only': True}
        }

    def validate(self, attrs):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError('Not authenticate!')

        attrs[self.Meta.user_field] = request.user
        return super().validate(attrs)


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('email', 'user_status', 'password')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        refresh = RefreshToken.for_user(user=instance)
        rep['id'] = instance.id
        rep['refresh'] = str(refresh)
        rep['access'] = str(refresh.access_token)
        return rep

    def create(self, validated_data):
        validated_data['username'] = str(uuid4())
        return super().create(validated_data)


class EntityProfilePhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityProfilePhone
        fields = ('phone',)


class EntityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityProfile
        fields = "__all__"
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def update(self, instance, validated_data):
        profile = instance
        request = self.context.get('request')
        for key, value in validated_data.items():
            setattr(profile, key, value)
        if request.user.user_status == 'entity':
            profile.is_moderation = False
            profile.is_active = False
        profile.save()

        requisites = request.data.get('entity_requisites')
        if requisites:
            EntityRequisite.objects.filter(profile=profile).delete()
            EntityRequisite.objects.bulk_create([EntityRequisite(profile=profile, **req) for req in requisites])

        phones = request.data.get('entity_phones')
        if phones:
            EntityProfilePhone.objects.filter(profile=profile).delete()
            EntityProfilePhone.objects.bulk_create([EntityProfilePhone(profile=profile, **pho) for pho in phones])

        personals = request.data.get('entity_personals')
        if personals:
            EntityPersonal.objects.filter(profile=profile).delete()
            EntityPersonal.objects.bulk_create([EntityPersonal(profile=profile, **per) for per in personals])

        elif profile.entity_phones.exists():
            EntityPersonal.objects.create(phone=profile.entity_phones.first().phone, full_name=profile.full_name,
                                          position=profile.position, email=profile.email, profile=profile)

        documents = request.data.get('entity_documents')
        if documents:
            Document.objects.filter(profile=profile).delete()
            Document.objects.bulk_create([Document(profile=profile, **doc) for doc in documents])

        return profile

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['entity_documents'] = DocumentSerializer(instance.entity_documents.all(),
                                                                    many=True, context=self.context).data
        representation['entity_personals'] = EntityPersonalSerializer(instance.entity_personals.all(),
                                                          many=True, context=self.context).data
        representation['entity_phones'] = EntityProfilePhoneSerializer(instance.entity_phones.all(),
                                                        many=True, context=self.context).data
        representation['entity_requisites'] = EntityRequisiteSerializer(instance.entity_requisites.all(),
                                                    many=True, context=self.context).data
        representation['comments'] = ProfileCommentSerializer(instance.comments.all(),
                                                              many=True, context=self.context).data
        representation['username'] = instance.user.username
        representation['useremail'] = instance.user.email
        representation['wallet'] = WalletSerializer(Wallet.objects.get(user=instance.user)).data
        representation['vacancies'] = MeVacancySerializer(instance.user.vacancies.all(), many=True,
                                                        context=self.context).data
        representation['all_history'] = EntityAllHistorySerializer(instance.user.all_history.all(), many=True,
                                                        context=self.context).data
        if instance.manager.exists():
            representation['manager'] = AdminManagerSerializer(instance.manager.first()).data

        return representation


class AdminManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['manager_username'] = instance.manager.username
        return representation


class ProfileCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileComment
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.manager:
            representation['manager_username'] = instance.manager.manager.username
        else: representation['manager_username'] = 'Менеджер удален'
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['manager'] = Manager.objects.get(manager=MyUser.objects.get(id=request.data.get('user')))
        comment = ProfileComment.objects.create(**validated_data)
        return comment

    def update(self, instance, validated_data):
        comment = instance
        request = self.context.get('request')
        validated_data['manager'] = Manager.objects.get(manager=MyUser.objects.get(id=request.data.get('user')))
        for key, value in validated_data.items():
            setattr(comment, key, value)
        comment.save()
        return comment


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('created_add', 'document')


class EntityPersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityPersonal
        fields = ('id', 'full_name', 'position', 'phone', 'email')

    def create(self, validated_data):
        request = self.context.get('request')
        profile = request.data.get('profile')
        validated_data['profile'] = EntityProfile.objects.get(id=profile)
        personal = EntityPersonal.objects.create(**validated_data)
        return personal

    def update(self, instance, validated_data):
        request = self.context.get('request')
        personal = instance
        profile = request.data.get('profile')
        validated_data['profile'] = EntityProfile.objects.get(id=profile)
        for key, value in validated_data.items():
            setattr(personal, key, value)
        personal.save()
        return personal


class EntityRequisiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityRequisite
        fields = ('id', 'entity_name', 'inn', 'okpo', 'mailing_address', 'entity_address', 'bik', 'bank_name',
                  'checking_account', 'gni', 'contact', 'email', 'info')


class EntityUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('email', 'user_status', 'username', 'id', 'image')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if EntityProfile.objects.filter(user=instance.id):
            rep['profile'] = EntityProfileSerializer(instance.entity_profile, context=self.context).data

        if Manager.objects.filter(profiles__user=instance.id):
            rep['manager'] = ManagerSerializer(instance.entity_profile.manager.all(), many=True, context=self.context).data

        if Vacancy.objects.filter(user=instance.id):
            rep['vacancies'] = VacancySerializer(instance.vacancies.all(), many=True, context=self.context).data
        rep['wallet'] = WalletSerializer(instance.wallet, context=self.context).data
        rep['favorites'] = EntityFavoriteSerializer(instance.favorite_resumes.all(), many=True, context=self.context).data

        return rep


class ApplicantUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('email', 'user_status', 'username', 'id', 'image')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['resumes'] = MeInfoResumeSerializer(instance.resume.all(), many=True).data
        rep['favorites'] = ApplicantFavoriteSerializer(instance.favorite_vacancies.all(), many=True, context=self.context).data

        return rep


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ('telegram', 'whatsapp', 'email')


class ApplicantImageUpdateSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.images)
        instance.save()
        return instance


class ApplicantFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantFavorite
        fields = ("vacancy", "favorite")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['vacancies'] = VacancySerializer(instance.vacancy, context=self.context).data
        return rep


class EntityFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = EntityFavorite
        fields = ("resume", "favorite")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['resume'] = ResumeSerializer(instance.resume, context=self.context).data
        return rep
    


