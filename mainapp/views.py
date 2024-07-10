import requests
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ObjectDoesNotExist
import json
from .models import CardDetail
# from .forms import CardDetailsForm
from django.http import JsonResponse
from datetime import datetime
from .forms import CustomUserCreationForm
from .models import Cryptocurrency, Portfolio, Profile, Referal
from django.views.decorators.csrf import csrf_exempt
# from .models import Purchase,CardDetail
from .models import PurchaseTransaction
from .models import CardDetail
from django.views.decorators.csrf import csrf_protect
# CardDetails


def login_view(request):
    # check if user is already logged in
    if request.user.is_authenticated:
        return redirect('portfolio')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('portfolio')
        else:
            messages.error(request, "Invalid username or password.", extra_tags='danger')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out!')
    return redirect('home')

def signup_view(request):
    # check if user is already logged in
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            
            if form.is_valid():
                user = form.save(commit=False)
                user.password = make_password(form.cleaned_data['password1'])
                user.email = form.cleaned_data['email']
                user.save()
                messages.success(request, 'You have successfully signed up!', extra_tags='success')
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


# block access to signup page if user is already logged in
def signup_with_referrer_view(request, referral_code):
    
    # check if user is already logged in
    if request.user.is_authenticated:
        return redirect('portfolio')
            
    try:
        # get the User Profile of the referrer
        referrer = User.objects.get(profile__referral_code=referral_code)
    except User.DoesNotExist:
        # show error message if referrer does not exist
        return HttpResponse("Referrer does not exist")

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password1'])
            user.email = form.cleaned_data['email']
            user.save()
            # create a referral instance
            referral = Referal.objects.create(user=user, referrer=referrer)
            referral.save()

            if referrer is not None:
                referrer.profile.bonus += 100  # add referral bonus to referrer
                referrer.profile.save()
                messages.success(request, f'{referrer.username} recieved a bonus of 100 points from you because you signed up using their referral link!')

            
            messages.success(request, 'You have successfully signed up!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form, 'referrer': referrer})



@login_required(login_url="login")
def portfolio_view(request):
    # get the current logged in user
    current_user = request.user

    try:
        # get the profile of the current user
        profile = current_user.profile

        # get the referal code of the current user
        referral_code = profile.referral_code

        # get total bonus earned by the current user
        total_bonus = profile.bonus

    except ObjectDoesNotExist:
        # Handle the scenario where the user does not have a profile
        referral_code = None
        total_bonus = None

    # get a list of all users who have the current user as their referrer
    referrals = Referal.objects.filter(referrer=current_user)

    # get the list of cryptocurrencies owned by the current user
    user_cryptocurrencies = Cryptocurrency.objects.filter(user=current_user)

    if user_portfolio := Portfolio.objects.filter(user=current_user).first():
        portfolio = Portfolio.objects.get(user=current_user)

        # get all the crypto currencies in the portfolio and recalculate the total value of the portfolio
        new_portfolio_value = 0

        user_cryptocurrencies = Cryptocurrency.objects.filter(user=current_user)
        for cryptocurrency in user_cryptocurrencies:
            total_value = cryptocurrency.quantity * cryptocurrency.current_price
            new_portfolio_value += total_value

        portfolio.total_value = new_portfolio_value
        portfolio.save()

        purchase_transactions = PurchaseTransaction.objects.filter(user=current_user)

        context = {
            'current_user': current_user,
            'referral_code': referral_code,
            'user_cryptocurrencies': user_cryptocurrencies,
            'user_portfolio': user_portfolio,
            'referrals': referrals, 
            'total_bonus': total_bonus,
            'new_portfolio_value': new_portfolio_value,
            'purchase_transactions': purchase_transactions,
        }
    else:
        context = {
            'current_user': current_user,
            'referral_code': referral_code,
            'user_cryptocurrencies': user_cryptocurrencies,
            'user_portfolio': user_portfolio,
            'referrals': referrals, 
            'total_bonus': total_bonus,
        }
    return render(request, 'portfolio.html', context)


def home_view(request):
    # get the top 10 crypto currencies by market cap
    top_10_crypto_url_global = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=10&page=1&sparkline=true'
    top_10_crypto_data_global = requests.get(top_10_crypto_url_global).json()

    # check if user is logged in    
    if request.user.is_authenticated:
        
        # get user's crypto currencies
        user_cryptocurrencies = Cryptocurrency.objects.filter(user=request.user)
        user_portfolio = Portfolio.objects.filter(user=request.user).first()
        
        # get the prices and price changes for user's cryptocurrencies
        names = [crypto.name for crypto in user_cryptocurrencies]
        symbols = [crypto.symbol for crypto in user_cryptocurrencies]
        ids = [crypto.id_from_api for crypto in user_cryptocurrencies]
        prices=[]
        
        # NOTE: Only showing the price change for the last 24 hours for now and not the percentage change to reduce the number of api calls. Only 10-20 api calls per minute are allowed for free users. Otherwise, I could have used the /coins/{id}/market_chart?vs_currency=usd&days=1 endpoint to get the price change for the last 24 hours and calculate the percentage change from that.
        for crytpo_id in ids:  
            prices_url = f'https://api.coingecko.com/api/v3/simple/price?ids={crytpo_id}&vs_currencies=usd&include_24hr_change=true'
            prices_data = requests.get(prices_url).json()

            price_change = prices_data[crytpo_id]['usd_24h_change']
            prices.append(price_change)
            
        # make a dictionary out of the names and prices
        crypto_price_changes = dict(zip(names, prices))
            
        context = {
            'top_10_crypto_data_global': top_10_crypto_data_global,
            'user_cryptocurrencies': user_cryptocurrencies,
            'user_portfolio': user_portfolio,
            'crypto_price_changes': crypto_price_changes,
        }
        
    else:
        context = {'top_10_crypto_data_global': top_10_crypto_data_global}    
    return render(request, 'home.html', context)


@login_required(login_url="login")
def search_view(request):
    if request.method != 'POST':
        # return HTTP status code 405 if the request method is not POST along with a message
        return HttpResponseNotAllowed(['POST'], 'Only POST requests are allowed for this view. Go back and search a cryptocurrency.')
    
    if not (search_query := request.POST.get('search_query')):
        return HttpResponse('No crypto currency found based on your search query.')
    
    api_url = f'https://api.coingecko.com/api/v3/search?query={search_query}'
    response = requests.get(api_url)
    search_results = response.json()
    try:
        data = search_results['coins'][0]
    except IndexError:
        return HttpResponse('No crypto currency found based on your search query.')
    coin_id = data['id']
    image = data['large']
    symbol = data['symbol']
    market_cap = data['market_cap_rank']

    # check if the crypto currency is already in the users portfolio and pass that information to the template
    current_user = request.user
    is_already_in_portfolio = False

    user_cryptocurrencies = Cryptocurrency.objects.filter(user=current_user)
    for cryptocurrency in user_cryptocurrencies:
        if cryptocurrency.name.lower() == coin_id.lower():
            is_already_in_portfolio = True    

    context = {
        'data': data,
        'coin_id': coin_id,
        'image': image,
        'symbol': symbol,
        'market_cap': market_cap,
        'is_already_in_portfolio': is_already_in_portfolio,
    }
    return render(request, 'search.html', context)
    
@login_required(login_url="login")
def add_to_portfolio_view(request):
    if request.method != 'POST':
        return HttpResponse('Need a crypto currency to add to your portfolio. Go back to the home page and search for a crypto currency.')
    
    # get values from the form
    coin_id = request.POST.get('id')
    quantity = request.POST.get('quantity')
    print(coin_id)
    
    # get the crypto currency data from the coingecko api based on the coin id
    api_url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
    response = requests.get(api_url)
    data = response.json()
    print(data)
    # store the name, symbol, current price, and market cap rank of the crypto currency
    user = request.user
    name = data['name']
    id_from_api = data['id']
    symbol = data['symbol']
    current_price = data['market_data']['current_price']['usd']

    try:
        # save the crypto currency to the database
        crypto_currency = Cryptocurrency.objects.create(
            user = user,
            name= name,
            id_from_api= id_from_api,
            symbol= symbol,
            quantity= quantity,
            current_price=current_price,
        )
    except IntegrityError:
        crypto_currency = Cryptocurrency.objects.get(user=user, name=name)
        crypto_currency.quantity += int(quantity)


    crypto_currency.save()

    # calculate the total value of the crypto currency
    total_value = int(quantity) * int(current_price)

    # save the total value of the crypto currency to the database in the portfolio model
    # check if the user already has a portfolio
    if Portfolio.objects.filter(user=user).exists():
        portfolio = Portfolio.objects.get(user=user)
        portfolio.total_value += total_value
    else: 
        portfolio = Portfolio(user=user, total_value=total_value)     

    portfolio.save()
    messages.success(request, f'{name} has been added to your portfolio.')

    # if all the above steps are successful, redirect the user to the portfolio page
    return redirect('portfolio') 
  
@login_required(login_url="login")      
def delete_from_portfolio_view(request, pk):
    # get the current logged in user
    user = request.user
    
    # get the crypto currency object from the database
    crypto_currency = Cryptocurrency.objects.get(pk=pk)
    
    # delete the crypto currency from the database
    crypto_currency.delete()
    
    # update the total value of the portfolio
    portfolio = Portfolio.objects.get(user=user)
    
    # get all the crypto currencies in the portfolio and recalculate the total value of the portfolio
    user_cryptocurrencies = Cryptocurrency.objects.filter(user=user)
    for cryptocurrency in user_cryptocurrencies:
        total_value = cryptocurrency.quantity * cryptocurrency.current_price
        portfolio.total_value += total_value
    
    portfolio.save()    

    # send an alert to the user that the crypto currency has been deleted from the portfolio
    messages.warning(request, f'{crypto_currency.name} has been deleted from your portfolio.')
    
    return redirect('portfolio')
    
def crypto_news_view(request):
    api_url = 'https://api.coingecko.com/api/v3/news'
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        news_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        news_data = []

    return render(request, 'crypto_news.html', {'news_data': news_data})

def crypto_exchange_rates_view(request):
    api_url = 'https://api.coingecko.com/api/v3/exchange_rates'
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        exchange_data = response.json().get('rates', {})
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        exchange_data = {}

    return render(request, 'crypto_exchange_rates.html', {'exchange_data': exchange_data})

def crypto_conversion_view(request):
    conversion_result = None
    if request.method == 'POST':
        coin1 = request.POST.get('coin1')
        coin2 = request.POST.get('coin2')
        
        # Fetch data for the first coin
        api_url_coin1 = f'https://api.coingecko.com/api/v3/simple/price?ids={coin1}&vs_currencies=usd'
        response_coin1 = requests.get(api_url_coin1)
        data_coin1 = response_coin1.json()
        
        # Fetch data for the second coin
        api_url_coin2 = f'https://api.coingecko.com/api/v3/simple/price?ids={coin2}&vs_currencies=usd'
        response_coin2 = requests.get(api_url_coin2)
        data_coin2 = response_coin2.json()
        
        if coin1 in data_coin1 and coin2 in data_coin2:
            price_coin1 = data_coin1[coin1]['usd']
            price_coin2 = data_coin2[coin2]['usd']
            conversion_rate = price_coin1 / price_coin2
            conversion_result = f"1 {coin1} is equal to {conversion_rate} {coin2}"

    return render(request, 'crypto_conversion.html', {'conversion_result': conversion_result})

def crypto_visualization_view(request):
    api_url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=max'

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Preprocess the data
        prices = data.get('prices', [])
        labels = [datetime.utcfromtimestamp(price[0] / 1000).strftime('%Y-%m-%d') for price in prices]
        prices = [price[1] for price in prices]

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        labels = []
        prices = []

    context = {
        'labels': json.dumps(labels),  # Convert to JSON string for JavaScript
        'prices': json.dumps(prices),  # Convert to JSON string for JavaScript
    }

    return render(request, 'crypto_visualization.html', context)




@csrf_protect
def card_details(request):
    if request.method == 'POST':
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        cvv = request.POST.get('cvv')
        
        card_detail = CardDetail(card_number=card_number, expiry_date=expiry_date, cvv=cvv)
        card_detail.save()
        
        return redirect('purchase_success')
    return render(request, 'card_details.html')


# def card_details(request):
#     return render(request, 'card_details.html')
def purchase_success(request):
    return render(request, 'purchase_success.html')
def purchase(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        currency = request.POST.get('currency')
        crypto_currency = request.POST.get('crypto_currency')
        crypto_amount = request.POST.get('crypto_amount')

        PurchaseTransaction.objects.create(
            amount=amount,
            currency=currency,
            crypto_currency=crypto_currency,
            crypto_amount=crypto_amount
        )
        # Perform your processing and redirect to card details page
        return redirect('card_details')
    
    return render(request, 'purchase.html')
    

# @csrf_exempt
def get_crypto_price(request):
    currency = request.GET.get('currency', 'usd')
    crypto_currency = request.GET.get('crypto_currency', 'bitcoin')
    
    # CoinGecko API endpoint for getting the current price
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_currency}&vs_currencies={currency}'
    
    try:
        response = requests.get(url)
        data = response.json()
        price = data[crypto_currency][currency]
        return JsonResponse({'price': price})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)