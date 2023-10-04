from django.urls import re_path
from django.conf.urls import url
from messenger import views
from rest_framework_jwt.views import (obtain_jwt_token, refresh_jwt_token,
                                      verify_jwt_token)
urlpatterns = [

    url(r'^auth/get-token', obtain_jwt_token),
    url(r'^auth/verify-token', verify_jwt_token),
    url(r'^auth/refresh-token', refresh_jwt_token),
    url(r'^users/$', views.UserListView.as_view()),
    url(r'^users/(?P<slug>[\w\-]+)/$', views.UserAPIView.as_view()),
    url(r'^activer_compte/(?P<slug>[\w\-]+)/$', views.AccountActivationAPIView.as_view()),
    url(r'^user_login/$', views.LoginView.as_view()),
    url(r'^supression_compte/$', views.SuppressionAPIListView.as_view()),
    url(r'^users_register/$', views.UserRegisterAPIView.as_view()),
    url(r'^send_message/$', views.SendMessageAPIView.as_view()),
    url(r'^list_message_sended/$', views.MessageListSendedAPIView.as_view()),
    url(r'^list_message_received/$', views.MessageListReceivedAPIView.as_view()),
    url(r'^message/(?P<slug>[\w\-]+)/$', views.MessageAPIView.as_view()),
    # ...
]
