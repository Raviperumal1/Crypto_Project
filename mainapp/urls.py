from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    
    # user authentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    path("signup/", views.signup_view, name="signup"),
    path('signup/<str:referral_code>/', views.signup_with_referrer_view, name='signup_with_referrer_view'),

    # wallet page
    path("portfolio/", views.portfolio_view, name="portfolio"),
    
    # CRUD operations on cryptos
    path("search/", views.search_view, name="search"),
    path("add_to_portfolio/", views.add_to_portfolio_view, name="add_to_portfolio"),
    path('delete_from_portfolio/<int:pk>/', views.delete_from_portfolio_view, name='delete_from_portfolio'),
    
    # password reset stuff
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="reset/password_reset.html"), name='password_reset'),
    
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name="reset/password_reset_done.html"), name='password_reset_done'),
    
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
    template_name='reset/password_reset_confirm.html'), name='password_reset_confirm'),

    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
    template_name='reset/password_reset_complete.html'), name='password_reset_complete'),
    path('crypto-news/', views.crypto_news_view, name='crypto_news'),
    path('crypto-exchange-rates/', views.crypto_exchange_rates_view, name='crypto_exchange_rates'),
    path('crypto-conversion/', views.crypto_conversion_view, name='crypto_conversion'),
    path('crypto_visualization/', views.crypto_visualization_view, name='crypto_visualization'),
    path('purchase/', views.purchase, name='purchase'),
    path('card-details/', views.card_details, name='card_details'),
    path('purchase-success/', views.purchase_success, name='purchase_success'),
    path('get-crypto-price/', views.get_crypto_price, name='get_crypto_price'),
]

