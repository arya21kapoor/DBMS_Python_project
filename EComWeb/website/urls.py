from django.urls import path
from . import views

app_name='website'

urlpatterns = [
    path('', views.homePageFunction, name="homePage" ),
    path('<slug:slug>/', views.categoryDetailFunction, name="category_detail" ),
    path('<slug:category_slug>/<slug:slug>/', views.productDetailFunction, name="productDetailFunction" ),
    path('add_to_cart/<slug:category_slug>/<slug:slug>/', views.add_to_cart, name="add_to_cart" ),
    path('remove_from_cart/<slug:category_slug>/<slug:slug>/', views.remove_from_cart, name="remove_from_cart" ),
]
