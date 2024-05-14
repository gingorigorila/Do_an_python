from django.urls import path
from authCart import views
urlpatterns = [
    path('login',views.handlelogin,name="handlelogin"),
    path('signup',views.signUp,name="signUp"),
    path('logout',views.logOut,name="logOut"),
    path('active/<uidb64>/<token>',views.ActiveAccountView.as_view(),name='active'),
    path('request-reset-email/',views.RequestResetEmailView.as_view(),name='request-reset-email'),
    path('set-new-password/<uidb64>/<token>',views.SetNewPasswordView.as_view(),name='set-new-password')
]