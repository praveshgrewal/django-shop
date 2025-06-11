from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib import messages
from django.http import HttpResponse
from .models import Product, CartItem,Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.db.models import Sum,F

# Create your views here.

def index_view(request):
    products = Product.objects.all()
    return render(request, 'store/index.html', {'products': products})

@login_required
def user_profile(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    orders = Order.objects.filter(user=user).order_by('-created_at')

    # Calculate total if missing
    for order in orders:
        total = order.items.annotate(
            item_total=F('product__price') * F('quantity')
        ).aggregate(total_amount=Sum('item_total'))['total_amount'] or 0

        print(f"Order ID: {order.id}, Total Amount: {total}")
        order.total_amount = total
        order.save()
        


    return render(request, 'store/user_profile.html', {
        'user': user,
        'cart_items': cart_items,
        'orders': orders,
    })
def product_detail_view(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, pk):
    product = Product.objects.get(pk=pk)
    cart_item, created = CartItem.objects.get_or_create(user = request.user,product = product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        item.total_price = item.product.price * item.quantity
    total = sum(item.total_price for item in cart_items)

    return render(request,'store/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if request.method == "POST":
        full_name = request.POST['full_name']
        address = request.POST['address']

        order = Order.objects.create(
            user = request.user,
            full_name = full_name,
            address = address,
            total_amount = 0
        )

        for cart_item in cart_items:
            OrderItem.objects.create(
                order = order,
                product = cart_item.product,
                quantity = cart_item.quantity
            )
            # Update total amount for the order
            order.total_amount = sum(
                item.product.price * item.quantity 
                for item in order.items.all()

            )
            order.save()
            cart_item.delete()  # Clear cart after order is placed
           
        return render(request,'store/order_success.html', {'order': order})
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request,'store/checkout.html',{
        'cart_items': cart_items,
        'total': total
    })

def register_view(reqeust):
    if reqeust.method == "POST":
        form = RegisterForm(reqeust.POST)
        if form.is_valid():
            form.save()
            messages.success(reqeust, "Registration successful! Please log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(reqeust, 'store/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'store/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')
