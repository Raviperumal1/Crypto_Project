from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

# Override the default User model to make the email unique
User._meta.get_field('email')._unique = True

# Make the profile for a user, automatically created when a user is created using Django signals
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=10, unique=True)
    bonus = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} profile'

# Create the referal model
class Referal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals')

    def __str__(self):
        return f'{self.user.username} was referred by {self.referrer.username}'

# Create the Cryptocurrency model
class Cryptocurrency(models.Model):
    # here name is also the id of the cryptocurrency, so useful for API calls
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cryptocurrencies', null=True)
    id_from_api = models.CharField(max_length=50)
    name = models.CharField(max_length=50) 
    symbol = models.CharField(max_length=10)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    
    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f'{self.name} ({self.symbol})'

# Create the portfolio linked to a user and store the total value of the portfolio
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    total_value = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f'{self.user.username} - Portfolio: {self.total_value}'

# from django.db import models
# from django.contrib.auth.models import User

# class Cryptocurrency(models.Model):
#     name = models.CharField(max_length=50)
#     symbol = models.CharField(max_length=10)

#     def __str__(self):
#         return self.name

# class Transaction(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     cryptocurrency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
#     amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
#     amount_crypto = models.DecimalField(max_digits=20, decimal_places=8)
#     transaction_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user} bought {self.amount_crypto} {self.cryptocurrency.symbol} for {self.amount_usd} USD"



# class CardDetail(models.Model):
#     purchase = models.OneToOneField(Transaction, on_delete=models.CASCADE)
#     card_number = models.CharField(
#         max_length=16, 
#         validators=[RegexValidator(r'^\d{16}$')],
#         help_text="Card number must be 16 digits"
#     )
#     expiry_date = models.CharField(
#         max_length=5,
#         validators=[RegexValidator(r'^\d{2}/\d{2}$')],
#         help_text="Expiry date must be in MM/YY format"
#     )
#     cvv = models.CharField(
#         max_length=3,
#         validators=[RegexValidator(r'^\d{3}$')],
#         help_text="CVV must be 3 digits"
#     )

#     def __str__(self):
#         return f"Card ending in {self.card_number[-4:]}"

# models.py

from django.db import models

# class CryptoCurrency(models.Model):
#     name = models.CharField(max_length=50)
#     code = models.CharField(max_length=10)
#     price = models.DecimalField(max_digits=20, decimal_places=8)

#     def __str__(self):
#         return self.name

class PurchaseTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Set default user ID here
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    crypto_currency = models.CharField(max_length=10)
    crypto_amount = models.DecimalField(max_digits=10, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.crypto_currency}"

# class CardDetails(models.Model):
#     card_number = models.CharField(max_length=16)
#     expiry_date = models.CharField(max_length=5)  # Assuming MM/YY format
#     cvv = models.CharField(max_length=3)

#     def __str__(self):
#         return self.card_number

    
class CardDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Set default user ID here
    card_number = models.CharField(max_length=16)
    expiry_date = models.CharField(max_length=5)
    cvv = models.CharField(max_length=3)
    

    def __str__(self):
        return f"Card ending in {self.card_number[-4:]}"