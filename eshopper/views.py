from django.shortcuts import HttpResponse,redirect,render
from django.http import response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from rest_framework.views import APIView
from .serializer import Loginserial
from api.models import CustomUser,product,contactus,Cart,categories,price_range,Order,blog
from django.conf import settings
import requests
from api.serializer import contactserializer
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

def home(request):
    slider_img=blog.objects.all()
    # extracted_images = []
    # for b in slider_img:
    #     # Use a regular expression to find all image src paths in the body
    #     img_srcs = re.findall(r'<img[^>]*src="([^"]+)"', b.body)
    #     extracted_images.append(img_srcs)
    cateid=request.GET.get('category')
    prcrng=request.GET.get('pricerange')
    low_price=0
    high_price=100000
    if prcrng:
        low_price, high_price = prcrng.split('-')
    if cateid:
        prd=product.objects.filter(category=cateid).filter(price__gte=low_price, price__lte=high_price)
    else:
        prd=product.objects.all().filter(price__gte=low_price, price__lte=high_price)
    cate=categories.objects.all()
    prc_range=price_range.objects.all()
    products_data = []
    for b in prd:
        # Calculate the discounted price using the method defined in the Product model
        discounted_price = b.discounted_price()

        # Store product information in a dictionary
        products_data.append({
            'id':b.id,
            'name': b.name,
            'img':b.img,
            'original_price': b.price,
            'discount_percentage': b.discount_percentage,
            'discounted_price': discounted_price,
            'category': b.category,  # Add category to the product data
        })
    
    data={
        'prd':products_data,
        'cate':cate,
        'prc_range':prc_range,
         'low_price': low_price,
        'high_price': high_price,
        'slider_img':slider_img
    }
    return render(request,'index.html',data)

def search(request):
    cateid=request.GET.get('category')
    query=request.GET['query']
    if cateid:
        prd=product.objects.filter(category=cateid)
    elif query:
        prd=product.objects.filter(name__icontains=query)
      
    else:
        prd=product.objects.all()
    cate=categories.objects.all()
    
    products_data = []
    for b in prd:
        # Calculate the discounted price using the method defined in the Product model
        discounted_price = b.discounted_price()

        # Store product information in a dictionary
        products_data.append({
            'id':b.id,
            'name': b.name,
            'img':b.img,
            'original_price': b.price,
            'discount_percentage': b.discount_percentage,
            'discounted_price': discounted_price,
            'category': b.category,  # Add category to the product data
        })
    print(products_data)
    data={
        'prd':products_data,
        'cate':cate,
        
    }
    return render(request,'index.html',data)
def signup(request):
    if request.method == 'POST':
        mail=request.POST.get('mail')
        fname=request.POST.get('fname')
        lname=request.POST.get('lname')
        age=request.POST.get('age')
        hobbie=request.POST.get('hobbie')
        gender=request.POST.get('gender')
        psw=request.POST.get('psw1')
        psw1=request.POST.get('psw2')
        
        recaptcha_response = request.POST.get('g-recaptcha-response')
        if not recaptcha_response:
            messages.error(request, "Please verify that you are not a robot.")
            return redirect('signup')
        # Verify the reCAPTCHA response with Google's API
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        response = requests.post(verify_url, data=data)
        result = response.json()
        if result['success']:
            if mail=="" or fname=="" or lname=="" or age == "" or hobbie=="" or psw=="" or psw1 == "":
                messages.error(request,"all fields are required")
                return redirect('signup')
            elif CustomUser.objects.filter(email=mail).exists():
                messages.error(request,"This email address is already exists..")
                return redirect('signup')
            elif psw!=psw1:
                messages.error(request,"Password is not match..")
                return redirect('signup')
            elif gender=="select":
                messages.error(request,"Please select gender")
                return redirect('signup')
            else:
                myuser=CustomUser.objects.create_user(email=mail,password=psw,first_name=fname,last_name=lname,age=age,hobbie=hobbie,gender=gender)
                myuser.save()
                myuser=authenticate(email=mail,password=psw)
                if myuser is not None:
                    login(request,myuser)
                    cart_cookie=request.COOKIES.get('cart','[]')
                    if cart_cookie:
                        cart_products=json.loads(cart_cookie)
                        for product_id in range(len(cart_products)):
                            try:
                                prd=product.objects.get(id=cart_products[product_id]['id'])
                                Cart.objects.create(
                                    user=request.user,
                                    cart_product=prd,
                                    quantity=cart_products[product_id]['quantity']
                                )
                            except product.DoesNotExist:
                                continue
                        response=redirect('cart_detail')
                        response.delete_cookie('cart')
                        return response
                    return redirect('home')
    return render(request,'signup.html')

def log_in(request):
    if request.method == 'POST':
        unm=request.POST.get('uname')
        psw=request.POST.get('psw')
        recaptcha_response = request.POST.get('g-recaptcha-response')
        if not recaptcha_response:
            messages.error(request, "Please verify that you are not a robot.")
            return redirect('login')
        # Verify the reCAPTCHA response with Google's API
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        response = requests.post(verify_url, data=data)
        result = response.json()
        if result['success']:
            myuser=authenticate(email=unm,password=psw)
            if myuser is not None:
                login(request,myuser)
                cart_cookie = request.COOKIES.get('cart', '[]')
                if cart_cookie:
                    cart_products = json.loads(cart_cookie)
                    for product_id in range(len(cart_products)):
                        try:
                            prd = product.objects.get(id=cart_products[product_id]['id'])
                            prd_user=Cart.objects.get(user=request.user,cart_product=prd) or None
                            if prd_user is None:
                                Cart.objects.create(
                                    user=request.user,
                                    cart_product=prd,
                                    quantity=cart_products[product_id]['quantity'],
                                )
                            else:
                                prd_user.quantity+=cart_products[product_id]['quantity']
                                prd_user.save()
                        except product.DoesNotExist:
                            continue  
                    response = redirect("cart_detail")
                    response.delete_cookie('cart') 
                    return response
                return redirect('home')
            else:
                messages.error(request,"username or password is wrong..")
                return redirect('login')
    return render(request,'login.html')

def log_out(request):
    logout(request)
    return redirect('login')


def contact(request):
    if request.method == 'POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        mobile=request.POST.get('mobile')
        subject=request.POST.get('subject')
        message=request.POST.get('message')
        con=contactus(name=name,email=email,mobile=mobile,subject=subject,message=message)
        con.save()
        send_mail(
                        'Thank You for Contacting Us',
                        f"Dear {name},\n\n"
                        "Thank you for reaching out to us. We have received your message and our team will get back to you as soon as possible.\n\n"
                        "Here are the details you submitted:\n"
                        f"Subject: {subject}\n"
                        f"Message: {message}\n\n"
                        "Best regards,\n"
                        "The Eshopper Team",
                        settings.DEFAULT_FROM_EMAIL,  
                        [email],  
                        fail_silently=False,
                    )
        messages.success(request,"your message is received..")
    return render(request,"contact-us.html")

import json
def cart_add(request, id):
    try:
        prd = product.objects.get(id=id)  
    except product.DoesNotExist:
        return redirect("home")
    if request.user.is_authenticated:
        existing_cart_item = Cart.objects.filter(user=request.user, cart_product=prd).first()
        if existing_cart_item:
            existing_cart_item.quantity += 1
            existing_cart_item.save()
        else:
            Cart.objects.create(
                user=request.user,
                cart_product=prd
            )
    else:
        cart_cookie = request.COOKIES.get('cart', '[]')  
        cart_products = json.loads(cart_cookie)
        product_found = False
        for product_id in range(len(cart_products)):
            cart_prdid = cart_products[product_id]['id']
            if cart_prdid == prd.id: 
                qty = cart_products[product_id]['quantity']
                cart_products[product_id]['quantity'] = qty + 1
                product_found = True
                break 
        if not product_found:
            cart_products.append({'id': prd.id, 'quantity': 1})

        response = redirect("home")
        print("Updated Cart Products:", cart_products) 
        response.set_cookie('cart', json.dumps(cart_products))
        print("Set Cookie in Response:", response.cookies)             
        return response
                      
    return redirect("home")


def item_clear(request, id):
    prd = product.objects.get(id=id)
    if request.user.is_authenticated:
        cart_item = Cart.objects.get(cart_product=prd, user=request.user)
        cart_item.delete()
    else:
        cart_cookie = request.COOKIES.get('cart', '[]')
        cart_products = json.loads(cart_cookie)

        updated_cart = [item for item in cart_products if item['id'] != prd.id]

        if len(updated_cart) != len(cart_products):
            response = redirect("cart_detail")  
            response.set_cookie('cart', json.dumps(updated_cart))  

            return response
    return redirect("cart_detail")


def item_increment(request, id):
    prd = product.objects.get(id=id)
    if request.user.is_authenticated:
        cart_item = Cart.objects.get(cart_product=prd, user=request.user)
        cart_item.quantity += 1  
        cart_item.save()

    else:        
        cart_cookie = request.COOKIES.get('cart', '[]')
        cart_products = json.loads(cart_cookie)
        for product_id in range(len(cart_products)):
            cart_prdid=cart_products[product_id]['id']
            if cart_prdid == prd.id:
                qty=cart_products[product_id]['quantity']
                cart_products[product_id]['quantity']=qty+1
                response = redirect("cart_detail")
                response.set_cookie('cart',json.dumps(cart_products))
                return response
            
    return redirect("cart_detail")


def item_decrement(request, id):
    prd = product.objects.get(id=id)
    if request.user.is_authenticated:
        cart_item = Cart.objects.get(cart_product=prd, user=request.user)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  
            cart_item.save()
    else:
        cart_cookie = request.COOKIES.get('cart', '[]')
        cart_products = json.loads(cart_cookie)
        for product_id in range(len(cart_products)):
            cart_prdid=cart_products[product_id]['id']
            if cart_prdid == prd.id:
                qty=cart_products[product_id]['quantity']
                cart_products[product_id]['quantity']=qty-1
                response = redirect("cart_detail")
                response.set_cookie('cart',json.dumps(cart_products))
                return response

    return redirect("cart_detail")


def cart_clear(request):
    if request.user.is_authenticated:
        Cart.objects.filter(user=request.user).delete() 
    else:
        response = redirect("cart_detail")
        response.delete_cookie('cart') 
        return response
    return redirect("cart_detail")


def cart_detail(request):
    if request.user.is_authenticated:
        items = Cart.objects.filter(user=request.user)
        total_price = 0 
        for k in items:
            k.finalprc=k.cart_product.discounted_price()*k.quantity
            total_price += k.finalprc
    else:
        cart_cookie = request.COOKIES.get('cart', '[]')
        cart_products = json.loads(cart_cookie)
        items = []
        for product_id in range(len(cart_products)):
            try:
                prd = product.objects.get(id=cart_products[product_id]['id'])
                finalprc = prd.discounted_price() * cart_products[product_id]['quantity']
                items.append({
                    'cart_product': prd,
                    'quantity': cart_products[product_id]['quantity'],  # Since we don't store quantities in the cookie, assume 1 per item
                    'finalprc': finalprc  
                })
            except product.DoesNotExist:
                continue  
        s=[]
        for a in items:
            c=a['finalprc']
            s.append(c)
        total_price=(sum(s))

    data={
        'items':items,
        'total_price':total_price
    }
    return render(request, 'cart.html',data)

#aa method ne whole project na koy pan template ma access kari sakay
def cart_item_count(request):
    total_items=0
    if request.user.is_authenticated:
        total_items = Cart.objects.filter(user=request.user).count() or 0
    else:
        cart_cookie = request.COOKIES.get('cart', '[]')
        cart_products = json.loads(cart_cookie)
        total_items=len(cart_products)

    return {'cart_item_count': total_items}

@login_required(login_url='login')
def checkout(request):
    if request.method == 'POST':
        add=request.POST.get('address')
        pho=request.POST.get('phone')
        pin=request.POST.get('pincode')
        items = Cart.objects.filter(user=request.user)
        if items:
            for i in items:
                ord=Order(
                    user=request.user,
                    ord_product=i.cart_product.name,
                    price=i.cart_product.discounted_price(),
                    quantity=i.quantity,
                    image=i.cart_product.img,
                    address=add,
                    phone=pho,
                    pincod=pin,
                    total=i.cart_product.discounted_price()*i.quantity
                )
                ord.save()
            items.delete()
            return redirect('home')
        else:
            messages.error(request,"add something in cart..")
            return redirect('cart_detail')
    return HttpResponse('this is checkout page.')

@login_required(login_url='login')
def yourorder(request):
    user=request.user
    ord=Order.objects.filter(user=user).values()
    data={
        'ord':ord,
    }
    return render(request,'yourorder.html',data)

@login_required(login_url='login')
def ordcancle(request, id):
    ord=Order.objects.filter(id=id)
    ord.delete()

    return redirect("yourorder")