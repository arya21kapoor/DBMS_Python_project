import random
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category, OrderItem, Order
from django.utils import timezone

def homePageFunction (request):
    products_list = Product.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(products_list, 6)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products
    }
    return render (request, 'homePage.html', context)


def productDetailFunction(request, category_slug, slug):
    product = get_object_or_404(Product, slug=slug)

    related_products = list(product.category.products.exclude(id=product.id))

    if len(related_products) > 4:
        related_products = random.sample(related_products, 4)

    context = {
    'product':product,
    'related_products': related_products
    }

    return render (request, 'productPage.html', context)

def categoryDetailFunction(request, slug):

    category = get_object_or_404(Category, slug = slug)
    products_list = category.products.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(products_list, 6)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products
    }
    return render (request, 'homePage.html', context)

def add_to_cart(request, category_slug, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user= request.user,
        # ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            #messages.info(request, "This item quantity was updated.")
            return redirect("website:productDetailFunction", slug = slug, category_slug = category_slug)
        else:
            order.items.add(order_item)
            #messages.info(request, "This item was added to your cart.")
            return redirect("website:productDetailFunction", slug = slug, category_slug = category_slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        #messages.info(request, "This item was added to your cart.")
        return redirect("website:productDetailFunction", slug = slug, category_slug = category_slug)


def remove_from_cart(request, category_slug, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                # ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            #messages.info(request, "This item quantity was updated.")

            order_qs = Order.objects.filter(user=request.user, ordered=False)

            if order_qs.exists():
                order = order_qs[0]

                if not order.items.exists():
                    order.delete()
                    return redirect("website:homePage")

            return redirect("website:productDetailFunction", slug = slug, category_slug = category_slug)
        else:
            #messages.info(request, "This item was not in your cart")
            return redirect("website:productDetailFunction", slug = slug, category_slug = category_slug)
    else:
        #messages.info(request, "You do not have an active order")
        return redirect("website:productDetailFunction", slug = slug, category_slug = category_slug)
