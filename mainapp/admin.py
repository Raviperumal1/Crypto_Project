from django.contrib import admin
from .models import Cryptocurrency, Portfolio, Profile, Referal, PurchaseTransaction, CardDetail

@admin.register(Referal)
class ReferalAdmin(admin.ModelAdmin):
    list_display = ('user', 'referrer')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'referral_code', 'bonus')

@admin.register(Cryptocurrency)
class CryptocurrencyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'id_from_api', 'symbol', 'current_price', 'quantity')

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_value')

@admin.register(PurchaseTransaction)
class PurchaseTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'crypto_currency', 'crypto_amount', 'timestamp')
    list_filter = ('currency', 'crypto_currency', 'timestamp')
    search_fields = ('currency', 'crypto_currency')

@admin.register(CardDetail)
class CardDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_number', 'expiry_date','cvv')
    search_fields = ('card_number',)
