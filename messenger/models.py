from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from safedelete.models import SafeDeleteModel
from safedelete.managers import SafeDeleteManager
from safedelete.config import DELETED_INVISIBLE 
from messenger.validators import *
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import JSONField
import uuid
from django.conf import settings
from messenger.utils import Utils as my_utils


ADMIN = 'admin'
USER = 'user'

SUPERADMIN = 'superadmin'
DELETED = 'deleted'
USER_TYPES = (
    (ADMIN, ADMIN),
    (USER, USER),
    (SUPERADMIN, SUPERADMIN),
  
    (DELETED, DELETED),
)
TEXT= 'text'
IMAGE = 'image'
VIDEO = 'video'
AUDIO = 'audio'
MSG_TYPE = (
    (TEXT, TEXT),
    (IMAGE, IMAGE),
    (VIDEO, VIDEO),
    (AUDIO, AUDIO),
)


BASIC = 'basic'
PREMIUM = 'premium'
ENTREPRISE = 'entreprise'

TYPE_ABONNEMENT = (
    (BASIC, BASIC),
    (PREMIUM, PREMIUM),
    (ENTREPRISE, ENTREPRISE),
)



ENVOIE = 'envoie'
RECEPTION= 'reception'
MESSAGERIE = 'messagerie'

NOTIF_TYPE= (
    (ENVOIE, ENVOIE),
    (RECEPTION, RECEPTION),
    (MESSAGERIE, MESSAGERIE),
)

class MyModelManager(SafeDeleteManager):
    _safedelete_visibility = DELETED_INVISIBLE

class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('user_type', SUPERADMIN)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
    


            
class User(AbstractBaseUser, PermissionsMixin, SafeDeleteModel):
    slug = models.SlugField(default=uuid.uuid1)
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=255, validators=[isalphavalidator])
    telephone = models.CharField(max_length=255, blank=True, null=True)
    user_type = models.CharField(max_length=255, choices=USER_TYPES, default=USER)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_archive = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    password_reset_count = models.IntegerField(blank=True, null=True)
    admin = models.BooleanField(default=False)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = my_utils.my_slugigy("user") 
            if User.objects.filter(slug=self.slug).exists():
                self.slug = "{slug}-{randstr}".format(
                    slug=self.slug,
                    randstr=my_utils.random_string_generator(size=5)
                )
        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        app_label = "messenger"
    
    def __str__(self):
        return str(self.email) + ''

class AdminUser(User):
    parent = models.ForeignKey(User,on_delete=models.CASCADE, related_name="admin_user_struc")
    admin_type = models.CharField(max_length=20, choices=USER_TYPES, default=ADMIN)
    created_at = models.DateTimeField(auto_now_add=True)
    dashboard=models.BooleanField(default=True)
    
    messagerie=models.BooleanField(default=True)
    missions_auth = models.BooleanField(default=True)
    parametre = models.BooleanField(default=True)

    def __str__(self):
        return str(self.email)

class AccountActivation(models.Model):
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    date_used = models.DateTimeField(null=True)
    pwd=models.CharField(max_length=1000,blank=True,null=True)

    def __str__(self):
        return f'<AccountActivation: {self.pk},user: {self.user},\
            used: {self.used}>'

class PasswordReset(SafeDeleteModel):
    code = models.CharField(max_length=7, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    date_used = models.DateTimeField(null=True)

    objects = MyModelManager()

    def __str__(self):
        return f'<PasswordReset: {self.pk},user: {self.user},\
            used: {self.used}>'
    
    def set_as_used(self):
        self.used = True
        self.date_used = timezone.now()
        self.save()


  


        

class Notification(SafeDeleteModel):
    slug = models.SlugField(default=uuid.uuid1)
    receiver = models.ForeignKey(User, related_name="receiver_notif",on_delete=models.CASCADE,
                                 blank=True, null=True)
    content = models.TextField()
    data = JSONField(null=True)
    notif_type = models.CharField(max_length=50, choices=NOTIF_TYPE, blank=True)
    is_archived = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    admins = models.ManyToManyField(User, default=[], blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    objects = MyModelManager()

    def __str__(self):
        return f'<Notification: {self.pk},receiver: {self.receiver},\
            content: {self.content},notif_type: {self.notif_type}>\
                read:{self.read}'

class Message(SafeDeleteModel):
    slug = models.SlugField(default=uuid.uuid1)
    sender = models.ForeignKey(User, related_name="sender_msg",on_delete=models.CASCADE,
                               blank=True)
    receiver = models.ForeignKey(User, related_name="receiver_msg",on_delete=models.CASCADE,
                                 blank=True)
    content = models.TextField()
    data = JSONField(null=True)
    msg_type = models.CharField(max_length=50, choices=MSG_TYPE, blank=True)
    is_archived = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    objects = MyModelManager()

    def __str__(self):
        return f'<Message: {self.pk},sender: {self.sender},\
            receiver: {self.receiver},content: {self.content},\
                msg_type: {self.msg_type},read:{self.read}>'
