from django.shortcuts import render
from rest_framework import generics, permissions, status
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate
import re
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from messenger.notifications import Notif as notify
from messenger.utils import REGEX, Utils as my_utils
from rest_framework_tracking.mixins import LoggingMixin
from messenger.admin import is_admin,get_admin_user
# Create your views here.

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class UserRegisterAPIView(LoggingMixin, generics.CreateAPIView):
    permission_classes = ()
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    REGEX_PATTERN = REGEX
    

    def do_after(self, item, user_type):
    
        """
        Perform actions after user registration.
        """
        contenu = f"Félicitations! Votre compte {user_type.upper()} sur SUNUCHAT vient d’être créé ! 🎉🎉"
        subject = "Bienvenu(e)🎉 sur SUNUCHAT"
        to = item.email
        template_src = 'mail_notification.html'
        context = {
            'user_type': user_type.upper(),
            'email': item.email,
            "fullname":item.fullname,
            "adresse":item.adresse,
            'settings': settings,
            "id":"false",
            "contenu":contenu,
            "year":timezone.now().year
        }
        notify.send_email(subject, to, template_src, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user registration.
        """
        pattern = re.compile(self.REGEX_PATTERN)
        if ('password' in request.data and request.data['password']
           and not pattern.match(request.data['password'])):
            return Response({ "message": "Le mot de passe doit avoir au moins au minimum 8 caractères,1 caractère en majuscule, 1 caractère en minuscule, 1 nombre et 1 caractère spéciale"
                    }, status=400)
        
        user_type = request.data.get("user_type")
        # if user_type == VENDEUR:
        #     return self.register_vendeur(request)
        if user_type == USER:
            return self.register_user(request)
        else:
            return Response({"message":"Veuillez choisir le type d'utilisateur vendeur ou user"}, status=400)

   


    def register_user(self, request):
        email = request.data.get("email")
        if User.objects.filter(email=email).first():
            return Response({"message":"Ce utilisateur existe déja dans la base de donnée"},status=400)
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        response = Response(UserGetSerializer(item).data, status=201)
        response._resource_closers.append(self.do_after(item, item.user_type))
        return response

    # def register_admin(self, request):
    #     email = request.data.get("email")
    #     if User.objects.filter(email=email).first():
    #         return Response({"message":"Ce utilisateur existe déja dans la base de donnée"},status=400)
    #     serializer = VendeurRegisterSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     item = serializer.save()
    #     response = Response(UserGetSerializer(item).data, status=201)
    #     response._resource_closers.append(self.do_after(item, VENDEUR))
    #     return response

# def is_vendeur(user):
#     # Vérifiez si l'utilisateur a l'attribut "user_type" égal à "vendeur"
#     return user.user_type == "vendeur"

class UserListView(LoggingMixin ,generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, slug, format=None):
        try:
            item = User.objects.get(slug=slug)
            if (request.user.id == item.id or request.user.is_superuser or
               request.user.user_type == ADMIN):
                serializer = UserGetSerializer(item)
                return Response(serializer.data)
            else:
                return Response({"message": "Accès interdit"}, status=401)
        except User.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = User.objects.get(slug=slug)
            if (request.user.id == item.id or request.user.is_superuser
               or request.user.user_type == ADMIN):
                self.data = request.data.copy()
                if 'password' in request.data:
                    item.set_password(request.data['password'])
                    self.data['password'] = item.password
                serializer = UserSerializer(item, data=self.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    item.save()
                    return Response(UserGetSerializer(item).data)
                return Response(serializer.errors, status=400)
            return Response({"message": "Accès interdit"}, status=401)
        except User.DoesNotExist:
            return Response(status=404)

    def delete(self, request, slug, format=None):
        try:
            item = User.objects.get(slug=slug)
            if request.user.is_superuser or request.user.user_type == ADMIN:
                self.handle_user_deletion(item)
                # item.delete(force_policy=HARD_DELETE)
                return Response(status=204)
            return Response({"message": "Accès interdit"}, status=401)
        except User.DoesNotExist:
            return Response(status=404)
    
    def handle_user_deletion(self, item):
        randomstring = my_utils.random_string_generator(12,"userdeletion")
        email = item.email
        user_type = item.user_type
        item.email = f"{randomstring}{item.email}"
        item.deletion_id = email
        item.user_type = DELETED
        item.is_active = False
        item.is_archive = True
        item.deletion_type = user_type
        item.save()


class LoginView(LoggingMixin ,generics.CreateAPIView):
    permission_classes = ()

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        if 'email' in request.data and request.data['email']:
            if 'password' in request.data and request.data['password']:
                try:
                    item = User.objects.get(email=request.data['email'])
                    user = authenticate(request, email=request.data['email'], password=request.data['password'])
                    if item.is_archive==True:
                        return Response({"message": "Votre compte a été désactivé, veuillez contacter l'administrateur"}, status=401)
                    elif item.is_active==False:
                        return Response({"status": "failure","message": "Votre compte n'est pas actif"}, status=401)
                    elif user and  user.is_active == True :
                        token = jwt_encode_handler(jwt_payload_handler(user))
                        if is_admin(user):
                            return Response({'token': token,'data':AdminUserSerializer(get_admin_user(user)).data}, status=200)
                        else:  
                            return Response({
                                'token': token,
                                'data':UserGetSerializer(user).data
                            }, status=200)
                    else:
                        return Response({"message":"Vos identifiants sont incorrects"},status=400)
                except User.DoesNotExist:
                    return Response({"status": "failure","message": "Ce compte n'existe pas. Veuillez vous s'inscrire"}, status=400)
            return Response({"message":"Votre mot de passe est requis"},status=401)
        return Response({"message":"Votre email est requis"},status=401)

class SuppressionAPIListView(LoggingMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SuppressionCompteSerializer

    def post(self, request, format=None):
        if 'password' in request.data and request.data['password']:
            item = User.objects.get(pk=request.user.id)
            
            password = request.data['password']
            user = authenticate(request, email=item.email, password=password)
            if user:
                email = item.email
                user_type=item.user_type
                fullname = item.fullname
                randomstring = my_utils.random_string_generator(
                    12, "userdeletion")
                item.email = randomstring+""+item.email
                item.deletion_id = email
                item.deletion_type = user_type
                item.user_type = DELETED
                item.is_active = False
                item.is_archive = True
                item.save()
                subject, to = "SUPPRESSION DE VOTRE COMPTE", email
                notify.send_email(subject, to, 'mail_suppression_user.html',
                                  {"fullname": fullname})
                return Response({"status": "success",
                                 "message": "user successfully deleted "},
                                status=200)
            return Response({"Le mot de passe est incorrect."}, status=400)
        return Response(
            {"Le mot de passe est requis pour supprimer votre compte"},
            status=401)

class AccountActivationAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AccountActivationSerializer

    def get(self, request, slug, format=None):
        try:
            item = User.objects.get(slug=slug)
            serializer = AccountActivationSerializer(item)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = AccountActivation.objects.get(slug=slug)
        except AccountActivation.DoesNotExist:
            return Response(status=404)
        serializer = AccountActivationSerializer(item, data=request.data,
                                                 partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = AccountActivation.objects.get(slug=slug)
        except AccountActivation.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class SendMessageAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        if 'content' in request.data and request.data['content']:
            item = User.objects.get(pk=request.user.id)
            receiver = User.objects.get(pk=request.data['receiver'])
            fullname = item.fullname
            email = item.email
            message = request.data['content']
            subject = "MESSAGE DE L'UTILISATEUR"
            to = receiver.email
            # print(to)
            
            request.data["sender"] = request.user.id
            serializer = MessageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            item = serializer.save()
            response = Response(MessageSerializer(item).data, status=201)
            notify.send_email(subject, to, 'mail_new_message.html',
                                {"fullname": fullname, "message": message})
                            
            return Response({"status": "success",
                                "message": "message successfully sent "},
                                status=200)
        else:
            return Response(
            {"Le message est requis pour envoyer votre message"},
            status=401)

class MessageListSendedAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = SendMessageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        messages = Message.objects.filter(sender=request.user.id)
        # messages = Message.objects.all()
        serializer = SendMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MessageListReceivedAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = ReceiveMessageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        messages = Message.objects.filter(receiver=request.user.id)
        # messages = Message.objects.all()
        serializer = ReceiveMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get(self, request, slug, format=None):
        try:
            item = Message.objects.get(slug=slug)
            serializer = MessageSerializer(item)
            return Response(serializer.data)
        except Message.DoesNotExist:
            return Response(status=404)

    def put(self, request, slug, format=None):
        try:
            item = Message.objects.get(slug=slug)
        except Message.DoesNotExist:
            return Response(status=404)
        serializer = MessageSerializer(item, data=request.data,
                                                 partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, slug, format=None):
        try:
            item = Message.objects.get(slug=slug)
        except Message.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)
    