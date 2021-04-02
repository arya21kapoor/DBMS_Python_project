from django.contrib import messages
from django.contrib.auth.decorators import login_required # used in functions
from django.contrib.auth.mixins import LoginRequiredMixin # used in Class Based Views
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.utils import timezone
from django.views.generic import View

import random
import stripe
from io import BytesIO
from xhtml2pdf import pisa

from .models import Product, Category, OrderItem, Order, Payment, Coupon, Address
from .forms import CouponForm, CheckoutForm
from .utils import random_string_generator


stripe.api_key = 'sk_test_51IXi0FSDx5m6eXW3KfjVvvE6Rf0YSo0qCNkvalLxYvmJZ6yozVZEkvJejNo3Fe6VkQ4Js1gGL3cfY4ssEGrcQVs400oRZwpHDg'


class HomePage(View):
    def get(self, *args, **kwargs):
        products_list = Product.objects.all()
        page = self.request.GET.get('page', 1)
        paginator = Paginator(products_list, 8)

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context = {'products': products}

        return render(self.request, 'homePage.html', context)


class CategoryDetail(View):
    def get(self, *args, **kwargs):
        category = get_object_or_404(Category, slug = kwargs['slug'])
        products_list = category.products.all()
        page = self.request.GET.get('page', 1)
        paginator = Paginator(products_list, 8)

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context = {
            'products': products
        }
        return render (self.request, 'homePage.html', context)


class ProductDetail(View):
    def get(self, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs['slug'])

        related_products = list(product.category.products.exclude(id=product.id))

        if len(related_products) > 4:
            related_products = random.sample(related_products, 4)

        context = {'product':product, 'related_products': related_products}

        return render (self.request, 'productPage.html', context)


@login_required
def add_to_cart(request, category_slug, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user= request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("website:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("website:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("website:order-summary")


@login_required
def remove_single_item_from_cart(request, category_slug, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            messages.info(request, "This item quantity was updated.")

            order_qs = Order.objects.filter(user=request.user, ordered=False)

            if order_qs.exists():
                order = order_qs[0]

                if not order.items.exists():

                    if order.shipping_address :
                        if not order.shipping_address.used :
                            order.shipping_address.delete()

                    if order.billing_address :
                        if not order.billing_address.used:
                            order.billing_address.delete()

                    messages.info(request, "Cart has been emptied.")
                    order.delete()
                    return redirect("website:home_page")

            return redirect("website:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("website:product_detail", slug = slug, category_slug = category_slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("website:product_detail", slug = slug, category_slug = category_slug)


@login_required
def remove_entire_from_cart(request, category_slug, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()

            if order_qs.exists():
                order = order_qs[0]

                if not order.items.exists():

                    if order.shipping_address :
                        if not order.shipping_address.used :
                            order.shipping_address.delete()

                    if order.billing_address :
                        if not order.billing_address.used:
                            order.billing_address.delete()

                    order.delete()
                    return redirect("website:home_page")

            messages.info(request, "This item was removed from your cart.")
            return redirect("website:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("website:product_detail", category_slug = category_slug, slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("website:product_detail", category_slug = category_slug,  slug=slug)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
                'couponform': CouponForm(),
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("website:home_page")


class AddCouponView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        return redirect("website:home_page")

    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                try:
                     coupon = Coupon.objects.get(coupon_code=code)

                     if not coupon.active:
                         messages.info(self.request, "Coupon is NOT Active")
                         return redirect("website:order-summary")

                     couponDiscount = coupon.amount

                     if order.get_total_without_coupon() - couponDiscount < 0:
                         messages.info(self.request, "Coupon not valid for this Bill Amount")
                         return redirect("website:order-summary")

                except ObjectDoesNotExist:
                    messages.info(self.request, "This coupon does not exist")
                    return redirect("website:order-summary")

                couponDiscount

                order.coupon = coupon
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("website:order-summary")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("website:home_page")
        messages.info(self.request, "Some Error has been encountered. Please contact owner.")
        return redirect("website:order-summary")


class RemoveCouponView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if not order.coupon:
                messages.info(self.request, "Coupon was not applied")
                return redirect("website:order-summary")

            order.coupon = None
            order.save()
            messages.info(self.request, "Coupon removed Successfully")
            return redirect("website:order-summary")
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("website:home_page")


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order,
                'checkoutForm': CheckoutForm(),
            }

            billing_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 'B',
                default = True
            )

            if billing_address_qs.exists():
                context.update({'default_billing_address': billing_address_qs[0]})

            shipping_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 'S',
                default = True
            )
            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})

            return render(self.request, 'checkout.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("website:home_page")

    def is_valid_form(self, values):
        for field in values:
            if field == '':
                return False
        return True

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if order.billing_address:
                return redirect("website:payment")

            if form.is_valid():

                old_default_billing = None
                old_default_shipping = None


                cleaned_data = form.cleaned_data
                use_default_shipping = cleaned_data.get('use_default_shipping')

                if use_default_shipping:
                    address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type = 'S',
                        default = True
                    )

                    if address_qs.exists():
                        shipping_address = address_qs[0]
                    else:
                        messages.info(self.request, "No default shipping address available")
                        return redirect('website:checkout')

                else:
                    shipping_address_1 = cleaned_data.get('shipping_address_1')
                    shipping_address_2 = cleaned_data.get('shipping_address_2')
                    shipping_city = cleaned_data.get('shipping_city')
                    shipping_state = cleaned_data.get('shipping_state')
                    shipping_zip = cleaned_data.get('shipping_zip')

                    if self.is_valid_form([shipping_address_1, shipping_address_2, shipping_city, shipping_state, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            address_1=shipping_address_1,
                            address_2=shipping_address_2,
                            city=shipping_city,
                            state = shipping_state,
                            zip = shipping_zip,
                            address_type='S'
                        )

                        set_default_shipping = cleaned_data.get('set_default_shipping')

                        if set_default_shipping:
                            address_qs = Address.objects.filter(
                                user = self.request.user,
                                address_type = 'S',
                                default = True
                            )

                            if address_qs.exists():
                                print(address_qs)
                                old_default_shipping = address_qs[0]
                                old_default_shipping.default = False

                            shipping_address.default = True
                    else:
                        messages.info(self.request, "Please fill in the required shipping address fields")
                        return redirect('website:checkout')

                same_billing_address = cleaned_data.get('same_billing_address')
                use_default_billing = form.cleaned_data.get('use_default_billing')

                if use_default_billing:
                    address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type = 'B',
                        default = True
                    )

                    if address_qs.exists():
                        billing_address = address_qs[0]

                        shipping_address.save()
                        billing_address.save()

                        order.shipping_address = shipping_address
                        order.billing_address = billing_address
                        order.save()
                        return redirect('website:payment')
                    else:
                        messages.info(self.request, "No default billing address available")
                        return redirect('website:checkout')

                elif same_billing_address:

                    shipping_address.save()

                    billing_address = Address(

                    user=self.request.user,
                    address_1=shipping_address.address_1,
                    address_2=shipping_address.address_2,
                    city=shipping_address.city,
                    state = shipping_address.state,
                    zip = shipping_address.zip,
                    address_type='B'
                    )

                    billing_address.save()

                    order.shipping_address = shipping_address
                    order.billing_address = billing_address
                    order.save()

                    return redirect('website:payment')

                else:
                    billing_address_1 = cleaned_data.get('billing_address_1')
                    billing_address_2 = cleaned_data.get('billing_address_2')
                    billing_city = cleaned_data.get('billing_city')
                    billing_state = cleaned_data.get('billing_state')
                    billing_zip = cleaned_data.get('billing_zip')

                    if self.is_valid_form([billing_address_1, billing_address_2, billing_city, billing_state, billing_zip]):

                        billing_address = Address(
                            user=self.request.user,
                            address_1=billing_address_1,
                            address_2=billing_address_2,
                            city=billing_city,
                            state = billing_state,
                            zip = billing_zip,
                            address_type='B'
                        )

                        set_default_billing = cleaned_data.get('set_default_billing')


                        if set_default_billing:
                            address_qs = Address.objects.filter(
                                user = self.request.user,
                                address_type = 'B',
                                default = True
                            )

                            if address_qs.exists():
                                old_default_billing = address_qs[0]
                                old_default_billing.default = False

                            billing_address.default = True


                        if old_default_shipping:
                            old_default_shipping.save()

                        if old_default_billing:
                            old_default_billing.save()

                        shipping_address.save()
                        billing_address.save()

                        order.shipping_address = shipping_address
                        order.billing_address = billing_address
                        order.save()

                        return redirect("website:payment")
                    else:
                        messages.info(self.request, "Please fill in the required billing address fields")
                        return redirect("website:payment")
            else:
                messages.warning(self.request, "Error in filling Form")
                return redirect("website:payment")
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("website:home_page")


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if not order.billing_address:
                messages.warning(self.request, "Shipping and Billing Address Missing")
                return redirect("website:checkout")

            context = {'order' : order}

            return render(self.request, "payment.html", context = context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("website:home_page")
        return redirect("website:home_page")

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("website:home_page")

        amount = int(order.get_grand_total() * 100)
        token = self.request.POST.get('stripeToken')

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="inr",
                source = token,
            )

            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_grand_total()
            payment.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment

            order.billing_address.used = True
            order.billing_address.save()
            order.shipping_address.used = True
            order.shipping_address.save()

            order.ordered_date = timezone.now()


            temp_num = random_string_generator()

            for _ in range(3):
                try:
                    order_qs = Order.objects.filter(order_unique_num = temp_num)
                except:
                    messages.warning(self.request, "Error, contact dev")
                else:
                    if order_qs.exists:
                        temp_num = random_string_generator()
                    else:
                        break

            order.order_unique_num = temp_num

            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("website:past-orders")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("website:home_page")
        #
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("website:home_page")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect("website:home_page")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("website:home_page")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("website:home_page")

        except stripe.error.StripeError as e:
            messages.warning(self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("website:home_page")

        except Exception as e:
            messages.warning(self.request, "A serious error occurred. We have been notifed.")
            return redirect("website:home_page")


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None




class ViewBillPdf(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order_qs = Order.objects.filter(
                user = self.request.user,
                order_unique_num = kwargs['unique_num']
            )

            if order_qs.exists():
                data = {"order": order_qs[0]}

                pdf = render_to_pdf('bill_template.html', data)

                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf')
                    filename = "Invoice_12341231.pdf"
                    content = f"inline; filename= {filename}"
                    download = request.GET.get("download")

                    if download:
                        content = f"attachment; filename= {filename}.pdf"
                        response['Content-Disposition'] = content
                    return response
                return response
            else:
                return redirect("website:home_page")
        except:
            messages.info(self.request, "Contact Dev since bill not there")
            return redirect("website:home_page")


class PastOrders(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            orders_all = Order.objects.filter(user=self.request.user, ordered=True).order_by('-ordered_date')
        except ObjectDoesNotExist:
            messages.info(self.request, "Some Error has occurred, we have been sent an email")
            return redirect("website:home_page")

        context = {"orders" : orders_all}

        return render(self.request, 'past_orders.html', context = context)
