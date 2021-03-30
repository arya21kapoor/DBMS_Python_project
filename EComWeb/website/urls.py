from django.urls import path
from .views import add_to_cart, remove_entire_from_cart, remove_single_item_from_cart
from .views import HomePage, CategoryDetail, ProductDetail, OrderSummaryView, CheckoutView, PaymentView, AddCouponView, RemoveCouponView, ViewBillPdf, PastOrders

app_name='website'

urlpatterns = [
    path('', HomePage.as_view(), name="home_page" ),
    path('bill/Invoice-<unique_num>', ViewBillPdf.as_view(), name='bill_pdf_view' ),
    path('past-orders/', PastOrders.as_view(), name='past-orders'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('add-coupon/', AddCouponView.as_view(), name='add_coupon'),
    path('remove-coupon/',RemoveCouponView.as_view(), name='remove_coupon'),
    path('<slug:slug>/', CategoryDetail.as_view(), name="category_detail" ),
    path('<slug:category_slug>/<slug:slug>/', ProductDetail.as_view(), name="product_detail" ),
    path('add_to_cart/<slug:category_slug>/<slug:slug>/', add_to_cart, name="add_to_cart" ),
    path('remove_entire_from_cart/<slug:category_slug>/<slug:slug>/', remove_entire_from_cart, name="remove_entire_from_cart" ),
    path('remove_single_item_from_cart/<slug:category_slug>/<slug:slug>/', remove_single_item_from_cart, name="remove_single_item_from_cart" ),
]
