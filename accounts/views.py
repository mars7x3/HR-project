from rest_framework import status, viewsets, mixins

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .permissions import IsAuthorPermission, IsMainPermission, ManagerIsAuthorPermission, PersonalIsAuthorPermission, \
    UserIsAuthorPermission
from .serializers import *
from .utils import send_new_pwd, generate_pwd


class VerificationCodeView(APIView):

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Введите пожалуйста почту!'}, status=status.HTTP_400_BAD_REQUEST)
        if MyUser.objects.filter(email=email).exists():
            return Response({'error': "Пользователь с такой почтой уже существует!"},
                            status=status.HTTP_400_BAD_REQUEST)

        # EmailAndCode.send_confirm_code(email)
        return Response({'detail': "Успешно!"}, status=status.HTTP_200_OK)


# class CheckEmailView(APIView):
#
#     def post(self, request):
#         email = request.data.get('email')
#         if not email:
#             return Response({'error': 'Email required!'}, status=status.HTTP_400_BAD_REQUEST)

        # activation_code = request.data.get('activation_code')
        # if not activation_code:
        #     return Response({'error': 'Activation code required!'}, status=status.HTTP_400_BAD_REQUEST)

        # email_code_q = EmailAndCode.objects.filter(email=email)

        # if not email_code_q.exists():
        #     return Response({'error': 'The user will not find!'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # email_code = email_code_q.first()
        # if activation_code == email_code.code:
        #     email_code.delete()
        #     return Response({'detail': "Activation code accepted."}, status=status.HTTP_200_OK)
        # return Response({'error': "Invalid activation code!"}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'detail': serializer.data}, status=status.HTTP_201_CREATED)


class DeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.delete()
        return Response({'detail': "Успешное удаление."}, status=status.HTTP_200_OK)


class ChangePwdView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_pwd = request.data.get('old_pwd')
        email = request.data.get('email')
        new_pwd = request.data.get('new_pwd')
        user = MyUser.objects.get(email=email)
        if user.check_password(old_pwd):
            send_new_pwd(new_pwd, email)
            user.set_password(new_pwd)
            user.save()
            PasswordTest.objects.create(username=user.username, password=new_pwd, email=email)
            return Response({'detail': "Успешный сброс пароля."}, status=status.HTTP_200_OK)
        return Response({'error': "Неверный старый пароль!"}, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': "Что-то пошло не так!"}, status=status.HTTP_400_BAD_REQUEST)

        if user.check_password(password):
            user.email = email
            user.save()
            return Response({'detail': "Почта успешно изменена."}, status=status.HTTP_200_OK)
        return Response({'error': "Неверный пароль!"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyForgotPwdView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Введите пожалуйста почту!'}, status=status.HTTP_400_BAD_REQUEST)
        EmailAndCode.send_confirm_code(email)
        return Response({'detail': "Код активации успешно отправлен."}, status=status.HTTP_200_OK)


class ForgotPwdView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Введиет пожалуйста почту!'}, status=status.HTTP_400_BAD_REQUEST)

        activation_code = request.data.get('activation_code')
        if not activation_code:
            return Response({'error': 'Отсутствует активационный код!'}, status=status.HTTP_400_BAD_REQUEST)

        email_code_q = EmailAndCode.objects.filter(email=email)

        if not email_code_q.exists():
            return Response({'error': 'Пользователь не найден!'}, status=status.HTTP_400_BAD_REQUEST)

        email_code = email_code_q.first()
        user = MyUser.objects.get(email=email)
        if activation_code == email_code.code:
            pwd = generate_pwd()
            user.set_password(pwd)
            user.save()
            PasswordTest.objects.create(username=user.username, password=pwd, email=email)
            send_new_pwd(pwd, email)
            email_code.delete()
            return Response({'detail': "Активационный код принят."}, status=status.HTTP_200_OK)
        return Response({'error': "Неверный активационный код!"}, status=status.HTTP_400_BAD_REQUEST)


class SelfUserView(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    user_field = 'user'
    permission_classes = [IsAuthenticated, IsAuthorPermission]

    def get_object(self):
        q = self.get_queryset().filter(**{self.user_field: self.request.user})
        if q.exists():
            return q.first()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)


class CustomView(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsAuthorPermission]


class EntityProfileViewSet(CustomView):
    queryset = EntityProfile.objects.all()
    serializer_class = EntityProfileSerializer


class EntityProfileListView(viewsets.ReadOnlyModelViewSet):
    queryset = EntityProfile.objects.all()
    serializer_class = EntityProfileSerializer


class EntityUserInfoView(mixins.ListModelMixin, viewsets.GenericViewSet):
    user_field = 'id'
    permission_classes = [IsAuthenticated, IsAuthorPermission]
    queryset = MyUser.objects.all()
    serializer_class = EntityUserInfoSerializer

    def get_object(self):
        q = self.get_queryset().filter(**{self.user_field: self.request.user.id})
        if q.exists():
            return q.first()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)


class ApplicantUserInfoView(mixins.ListModelMixin, viewsets.GenericViewSet):
    user_field = 'id'
    permission_classes = [IsAuthenticated, IsAuthorPermission]
    queryset = MyUser.objects.all()
    serializer_class = ApplicantUserInfoSerializer

    def get_object(self):
        q = self.get_queryset().filter(**{self.user_field: self.request.user.id})
        if q.exists():
            return q.first()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)


class ApplicantImageView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        instance = MyUser.objects.get(id=request.user.id)
        instance.image = request.data.get('image')
        instance.save()
        return Response({"detail": 'Успешно изменено.'}, status=status.HTTP_200_OK)


class EntityPersonalViewSet(CustomView):
    queryset = EntityPersonal.objects.all()
    serializer_class = EntityPersonalSerializer
    permission_classes = [IsAuthenticated, PersonalIsAuthorPermission]


class EntityPersonalListView(viewsets.ReadOnlyModelViewSet):
    queryset = EntityPersonal.objects.all()
    serializer_class = EntityPersonalSerializer


class ProfileImageUpdateView(APIView):
    permission_classes = [IsAuthenticated, UserIsAuthorPermission]

    def put(self, request):
        image = request.data.get('image')
        profile = request.data.get('profile')
        profile = EntityProfile.objects.get(id=profile)
        profile.image = image
        profile.save()
        return Response({"data": "Успешно!"}, status=status.HTTP_200_OK)

    def delete(self, request):
        profile = request.data.get('profile')
        profile = EntityProfile.objects.get(id=profile)
        profile.image.delete()
        profile.save()
        return Response({"data": "Успешно!"}, status=status.HTTP_200_OK)


class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated, ManagerIsAuthorPermission]

    def put(self, request):
        image = request.data.get('image')
        profile = request.data.get('profile')
        profile = EntityProfile.objects.get(id=profile)
        profile.image = image
        profile.save()
        return Response({"data": "Успешно!"}, status=status.HTTP_200_OK)

    def delete(self, request):
        profile = request.data.get('profile')
        profile = EntityProfile.objects.get(id=profile)
        profile.image.delete()
        profile.save()
        return Response({"data": "Успешно!"}, status=status.HTTP_200_OK)


class ProfileCommentView(viewsets.ModelViewSet):
    queryset = ProfileComment.objects.all()
    serializer_class = ProfileCommentSerializer
    permission_classes = [IsAuthenticated, ManagerIsAuthorPermission]


class EntityRequisiteDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAuthorPermission]

    def post(self, request):
        requisite = request.data.get('requisite')
        queryset = EntityRequisite.objects.filter(id=requisite)
        if queryset:
            queryset.first().delete()
        return Response({"detail": "Успешно!"}, status=status.HTTP_200_OK)


class HRGroupPersonalListView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def get(self, request):
        main = MyUserSerializer(MyUser.objects.filter(user_status='main'), many=True).data
        manager = MyUserSerializer(MyUser.objects.filter(user_status='manager'), many=True).data
        moderator = MyUserSerializer(MyUser.objects.filter(user_status='moderator'), many=True).data

        return Response({"main": main, "manager": manager, "moderator": moderator}, status=status.HTTP_200_OK)


class HRGroupPersonalDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def post(self, request):
        user = MyUser.objects.get(id=request.data.get('user'))
        user.delete()
        return Response({'detail': "Удалено."}, status=status.HTTP_200_OK)


class HRGroupPersonalUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsMainPermission]

    def post(self, request):
        manager = Manager.objects.get(manager__id=request.data.get('user'))
        email = request.data.get('email')
        whatsapp = request.data.get('whatsapp')
        telegram = request.data.get('telegram')
        user = MyUser.objects.get(id=request.data.get('user'))
        user.email = email
        user.save()
        manager.email = email
        manager.whatsapp = whatsapp
        manager.telegram = telegram
        manager.save()
        return Response({'detail': "Изменено."}, status=status.HTTP_200_OK)


class CheckNoStatusUserView(APIView):
    list_user = ['applicant', 'entity', 'main']

    def get(self, request):
        data = []
        user = MyUser.objects.all()
        for u in user:
            if u.user_status not in self.list_user:
                data.append({u.id: u.email})

        return Response({"data": data}, status=status.HTTP_200_OK)

