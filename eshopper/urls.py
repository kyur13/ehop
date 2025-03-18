"""
URL configuration for eshopper project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from eshopper import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',views.home,name='home'),
    path('search/',views.search,name='search'),
    path('',views.home,name='home'),
    path('login/',views.log_in,name='login'),
    path('logout/',views.log_out,name='logout'),
    path('signup/',views.signup,name='signup'),
    path('contact/',views.contact,name='contactus'),
    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/', views.item_clear, name='item_clear'),
    path('cart/item_increment/<int:id>/', views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/', views.item_decrement, name='item_decrement'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('yourorder/', views.yourorder, name='yourorder'),
    path('yourorder/cancle/<str:id>/', views.ordcancle, name='ordcancle'),
    path('ckeditor/',include('ckeditor_uploader.urls'))
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
    urlpatterns+=static(settings.STATIC_URL,document_root = settings.STATIC_ROOT)