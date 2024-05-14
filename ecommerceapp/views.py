from django.http import HttpResponse
from math import ceil
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View
from ecommerceapp.models import Contact, Product, OrderUpdate, Orders

# Create your views here.
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

bot = ChatBot('chatbot', read_only=False, logic_adapters=[
              'chatterbot.logic.BestMatch'])

list_to_train = [
    "Tên cửa hàng là gì",
    "Thế giới balo",
    "Cửa hàng bạn bán gì",
    "Bán balo",
    "Ngoài balo bạn còn bán sản phẩm khác không",
    "Không có",
    "Đối tượng chính bạn nhắm tới là gì",
    "Học sinh hoặc sinh viên"
]

list_trainer = ListTrainer(bot)
list_trainer.train(list_to_train)


def index(request):
    allProducts = []
    category_Products = Product.objects.values('category', 'id')
    cats = {item['category'] for item in category_Products}
    for cat in cats:
        product = Product.objects.filter(category=cat)
        n = len(product)
        nSlides = n//4 + ceil((n/4) - (n//4))
        allProducts.append([product, range(1, nSlides), nSlides])
    params = {'allProducts': allProducts}

    return render(request, "index.html", params)


# def base(request):
#     allProducts1 = []
#     category_Products1 = Product.objects.values('category', 'id')
#     cats1 = {item['category'] for item in category_Products1}
#     for cat in cats1:
#         product1 = Product.objects.filter(category=cat)
#         n1 = len(product1)
#         nSlides1 = n1//4 + ceil((n1/4) - (n1//4))
#         allProducts1.append([product1, range(1, nSlides1), nSlides1])
#     params = {'allProducts1': allProducts1}

#     return render(request, "base.html", params)


def about(request):
    return render(request, "about.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        desc = request.POST.get("desc")
        pnumber = request.POST.get("pnumber")
        myquerry = Contact(name=name, email=email,
                           desc=desc, phone_number=pnumber)
        myquerry.save()
        messages.info(request, "Đã tiếp nhận thông tin. Xin đợi phản hồi")
        return render(request, "contact.html")

    return render(request, "contact.html")


def search(request):
    # if request.method == "POST":
    #     nameFind = request.POST.get("name")
    #     allProducts = []
    # category_Products = Product.objects.values('product_name', 'id')
    # cats = {item['product_name'] for item in category_Products}
    # for name in cats:
    #     product = Product.objects.filter(product_name=nameFind)
    #     n = len(product)
    #     nSlides = n//4 + ceil((n/4) - (n//4))
    #     allProducts.append([product, range(1, nSlides), nSlides])
    # params = {'allProducts': allProducts}
    if request.method == "POST":
        nameFind = request.POST.get("name")
        allProducts = []
        product = Product.objects.filter(product_name=nameFind)
        n = len(product)
        nSlides = n//4 + ceil((n/4) - (n//4))
        allProducts.append([product, range(1, nSlides), nSlides])
        params = {'allProducts': allProducts}
    return render(request, "index.html", params)


class detail(View):
    def get(self, request, id):
        product = Product.objects.filter(id=id)
        params = {'id': product}
        return render(request, "ProductDetail.html", params)


class filterBalo(View):
    def get(self, request, type):
       
        product = Product.objects.filter(category=type)
        params = {'category': product}
        return render(request, "productFilter.html", params)


def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(
            request, "Vui lòng đăng nhập hoặc đăng ký trước khi thanh toán")
        return redirect('/auth/login')
    else:
        if request.method == "POST":
            items_json = request.POST.get("itemsJson", '')
            name = request.POST.get("name")
            amount = request.POST.get('amt')
            email = request.POST.get("email")
            address = request.POST.get("address")
            pnumber = request.POST.get("phone")
            city = request.POST.get("city")
            state = request.POST.get("state")
            Order = Orders(items_json=items_json, name=name, amount=amount,
                           email=email, address=address, city=city, state=state, phone=pnumber)
            print(amount)
            Order.save()
            update = OrderUpdate(order_id=Order.order_id,
                                 update_desc="Đơn hàng đã được đặt")
            update.save()

            id = Order.order_id
            oid = str(id)+"BaloCenter"
            rid = oid.replace("BaloCenter", "")
            filter2 = Orders.objects.filter(order_id=rid)
            for post1 in filter2:
                post1.oid = oid
                post1.paymentstatus = "Chưa trả"
                post1.save()
    return render(request, "checkout.html")


def chatbot(request):
    return render(request, "chatbot.html")


def getResponse(request):
    userMsg = request.GET.get('userMsg')
    chatResponse = str(bot.get_response(userMsg))
    return HttpResponse(chatResponse)


def profile(request):
    if not request.user.is_authenticated:
        messages.warning(
            request, "Vui lòng đăng nhập hoặc đăng ký trước khi thanh toán")
        return redirect('/auth/login')
    currentUser = request.user.username
    items = Orders.objects.filter(email=currentUser)
    rid = 0
    for i in items:
        myid = i.oid
        rid = myid.replace("BaloCenter", "")
        print(rid)
    if rid != 0:
        status = OrderUpdate.objects.filter(order_id=int(rid))
    else:
        status = ""
    context = {"items": items, "status": status}
    return render(request, "Profile.html", context)
