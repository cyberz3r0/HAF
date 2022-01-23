from unicodedata import decimal
from django.http import request
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import Order, User, UserManager, Order, Friend, Item
import bcrypt

def index(request):
    
    return render(request,'index.html')

def register(request):
    
    return render(request,'register.html')

def history(request):
    context= {
        'user': User.objects.get(id=request.session['login_user']),
        'orders': Order.objects.all
    }
    return render(request,'history.html', context)

def login(request):
    user = User.objects.filter(email = request.POST['email'])
    if user:
        login_user = user[0]
    if bcrypt.checkpw(request.POST['password'].encode(), login_user.password.encode()):
        request.session['login_user'] = login_user.id
    return redirect('/history')


def processregister(request):
    errors = User.objects.validator(request.POST)
    if errors:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/register')
    
    else:
        pw_hash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        User.objects.create(
            first_name = request.POST['fname'],
            last_name = request.POST['lname'],
            email = request.POST['email'],
            password = pw_hash,
        )
    return redirect('/')

def logout(request):
    request.session.flush()
    return redirect('/')

def profile(request):
    context= {
        'user': User.objects.get(id=request.session['login_user']),
    }
    return render(request,'account.html',context)

def editfriends(request):
    context= {
        'user': User.objects.get(id=request.session['login_user']),
    }
    return render(request,'friends.html',context)

def addfriend(request):
    
    Friend.objects.create(
        name = request.POST['name'],
        created_by = User.objects.get(id=request.session['login_user']),
    )
    return redirect('/managefriends')

def removefriend(request,friend_id):
    friend = Friend.objects.get(id=friend_id)
    friend.delete()
    return redirect('/managefriends')
# *********************************************************************************************
def editorder(request, order_id):
    
    loggeduser = User.objects.get(id=request.session['login_user'])
    user_list = Friend.objects.all().values_list('name', flat=True)
    order = Order.objects.get(id=order_id)
    # request.session['number_of_food_items'] = fooditems
    
    
    context={
            'user': User.objects.get(id=request.session['login_user']),
            'friends': Friend.objects.all,
            'items': order.items.all,
            'order': Order.objects.get(id=order_id)
        }
    ###############Create User in friends list if not in list
    if loggeduser.first_name not in user_list:
        Friend.objects.create(
        name = loggeduser.first_name,
        created_by = User.objects.get(id=request.session['login_user']),
        )
    
    return render(request,'editorder.html', context)
# **************************************************************************************************
def processupdated(request, order_id):
    
    order = Order.objects.get(id=order_id)
    arr=[]
    costarr=[]
    itemnamearr=[]
    index = 0
    index2 = 0
    foodname=""
    cost_of_food= 0.00
    
    for item in order.items.all():
        if index == 0:
            index = int(item.id)
            index2= int(item.id)
        
    
    totalcost=0
    print(request.POST)
    
    
    #############find all unique friend IDs in Order and all the values of Items in an Order. 
    for key, value in request.POST.items():
        if key == "food_name"+str(index):
            itemnamearr.append(value)
        if key == "cost"+str(index):
            costarr.append(value)
        if key == "friends"+str(index):
            index+=1
            if value not in arr:
                arr.append(value)
        
    request.session['friends_in_order'] = arr
    
    #############Finding the total cost 
    for i in costarr:
        totalcost=float(i)+totalcost
    
    ##############finding grand total
    tip = float(request.POST['tip'])
    sales_tax = float(request.POST['sales_tax'])
    sales_tax1 = float(1+(sales_tax/100))
    grand_total = (tip) + (totalcost * sales_tax1)
    
    #############Update Order table
    
    order.name = request.POST['restaurant'],
    order.total_cost = totalcost
    order.tip = tip
    order.sales_tax = sales_tax
    order.grand_total = grand_total
    order.save()
    
    ##############Adding friends to the order
    # for friend in request.session['friends_in_order']:
        
    #     thisfriend = Friend.objects.get(id = friend)
    #     thisorder = Order.objects.last()
    #     thisorder.friends.add(thisfriend)
    
    ##############Adding all items in Order 
    for key, value in request.POST.items():
        print(index2)
        item=Item.objects.get(id=index2)
        if key == "food_name"+str(index2):
            foodname = value
        print(foodname)
        if key == "cost"+str(index2):
            cost_of_food = value
        print(cost_of_food)
        if key == "friends"+str(index2):
            index2+=1
            item.name= foodname
            item.cost = cost_of_food
            item.ordered_by_friend = Friend.objects.get(id=value) 
            item.save()
    return redirect (f'/updateorder/{order_id}')

def updatedresults(request, order_id):
    owe_money = {}
    friendarr = []
    request.session['owe_money'] = []
    previous = round(0.00,2)
    order = Order.objects.get(id=order_id)
    print(request.POST)
    context={
        'user': User.objects.get(id=request.session['login_user']),
        'friends': Friend.objects.all,
        'order': order
        
    
    }
    #############Creating unique user list 
    for item in order.items.all().order_by('ordered_by_friend'):
        name = item.ordered_by_friend.name
        if name not in friendarr:
            friendarr.append(name)
    #############Creating dictionary of users and what they owe (subtotal)
    for item in order.items.all().order_by('ordered_by_friend'):
        for x in range(len(friendarr)):
            if friendarr[x] == item.ordered_by_friend.name:
                if item.ordered_by_friend.name not in owe_money:
                    owe_money[item.ordered_by_friend.name] = float(round(item.cost,2)) 
                else:
                    previous = owe_money[item.ordered_by_friend.name]
                    owe_money[item.ordered_by_friend.name] = float(round(item.cost,2)) + previous
            
    #############Updating dictionary above with grand total owed to user (subtotal+tip and sales tax)
    party = len(friendarr)
    sales_tax = float(order.sales_tax)
    sales_tax1 = float(1+(sales_tax/100))
    tip = float(order.tip)
    for key, value in owe_money.items():
        value1 = (value * sales_tax1) + (tip/party)
        owe_money[key] = format(value1, ".2f")
    
    request.session['owed_money'] = owe_money
    return render(request,'results.html', context)

def ordersetup2(request,fooditems):
    
    loggeduser = User.objects.get(id=request.session['login_user'])
    user_list = Friend.objects.all().values_list('name', flat=True)
    request.session['number_of_food_items'] = fooditems
    
    
    context={
            'user': User.objects.get(id=request.session['login_user']),
            'friends': Friend.objects.all,
            'range': range(fooditems)
        }
    ###############Create User in friends list if not in list
    if loggeduser.first_name not in user_list:
        Friend.objects.create(
        name = loggeduser.first_name,
        created_by = User.objects.get(id=request.session['login_user']),
        )
    
    return render(request,'ordersetup2.html', context)

def processresults(request):
    arr=[]
    costarr=[]
    itemnamearr=[]
    index = int()
    index2= 0
    totalcost=0
    # print(request.POST)
    
    
    #############find all unique friend IDs in Order and all the values of Items in an Order. 
    for key, value in request.POST.items():
        if key == "food_name"+str(index):
            itemnamearr.append(value)
        if key == "cost"+str(index):
            costarr.append(value)
        if key == "friends"+str(index):
            index+=1
            if value not in arr:
                arr.append(value)
        
    request.session['friends_in_order'] = arr
    
    #############Finding the total cost 
    for i in costarr:
        totalcost=float(i)+totalcost
    
    ##############finding grand total
    tip = float(request.POST['tip'])
    sales_tax = float(request.POST['sales_tax'])
    sales_tax1 = float(1+(sales_tax/100))
    grand_total = (tip) + (totalcost * sales_tax1)
    
    #############Creating Order table
    Order.objects.create(
        name = request.POST['restaurant'],
        creator = User.objects.get(id=request.session['login_user']),
        total_cost = totalcost,
        tip = tip,
        sales_tax = sales_tax,
        grand_total = grand_total
    )
    
    ##############Adding friends to the order
    for friend in request.session['friends_in_order']:
        
        thisfriend = Friend.objects.get(id = friend)
        thisorder = Order.objects.last()
        thisorder.friends.add(thisfriend)
    
    ##############Adding all items in Order 
    for key, value in request.POST.items():
        
        if key == "food_name"+str(index2):
            foodname = value
        if key == "cost"+str(index2):
            cost_of_food = value
        if key == "friends"+str(index2):
            index2+=1
            Item.objects.create(
            name= foodname,
            cost = cost_of_food,
            order = Order.objects.last(),
            ordered_by_friend = Friend.objects.get(id=value) 
            )
        
    
    return redirect('/results')

def results(request):
    owe_money = {}
    friendarr = []
    request.session['owe_money'] = []
    previous = round(0.00,2)
    order = Order.objects.last()
    context={
        'user': User.objects.get(id=request.session['login_user']),
        'friends': Friend.objects.all,
        'order': Order.objects.last()
        
    
    }
    #############Creating unique user list 
    for item in order.items.all().order_by('ordered_by_friend'):
        name = item.ordered_by_friend.name
        if name not in friendarr:
            friendarr.append(name)
    #############Creating dictionary of users and what they owe (subtotal)
    for item in order.items.all().order_by('ordered_by_friend'):
        for x in range(len(friendarr)):
            if friendarr[x] == item.ordered_by_friend.name:
                if item.ordered_by_friend.name not in owe_money:
                    owe_money[item.ordered_by_friend.name] = float(round(item.cost,2)) 
                else:
                    previous = owe_money[item.ordered_by_friend.name]
                    owe_money[item.ordered_by_friend.name] = float(round(item.cost,2)) + previous
            
    #############Updating dictionary above with grand total owed to user (subtotal+tip and sales tax)
    party = len(friendarr)
    sales_tax = float(order.sales_tax)
    sales_tax1 = float(1+(sales_tax/100))
    tip = float(order.tip)
    for key, value in owe_money.items():
        value1 = (value * sales_tax1) + (tip/party)
        owe_money[key] = format(value1, ".2f")
    
    request.session['owed_money'] = owe_money
    return render(request,'results.html',context)


