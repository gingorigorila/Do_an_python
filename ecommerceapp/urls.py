from django.urls import path
from ecommerceapp import views
urlpatterns = [
    path('', views.index, name="index"),
    path('checkout', views.checkout, name="Checkout"),
    path('search', views.search, name="search"),
    path('about', views.about, name="about"),
    path('chatbot', views.chatbot, name="chatbot"),
    path('profile', views.profile, name="profile"),
    path('getResponse', views.getResponse, name="getResponse"),
    path('product/<id>', views.detail.as_view(), name="details"),
    path('balo/<type>', views.filterBalo.as_view(), name="filters"),
]
