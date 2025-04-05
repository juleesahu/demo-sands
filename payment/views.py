# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay
from razorpay.errors import SignatureVerificationError

from cart.cart import Cart
from cart.models import Order, OrderItem
from store.models import Product
from users.models import ShippingAddress, Profile

# Initialize Razorpay client
from .razorpay import razorpay_client

@csrf_exempt
def payment(request):
    cart_instance = Cart(request)
    cart_items = cart_instance.get_prods()
    cart_quantities = cart_instance.get_quants()
    total_quantity = sum(cart_quantities.values())
    order_total = cart_instance.order_total()

    shipping = ShippingAddress.objects.get(user=request.user)
    
    request.session['shipping'] = {
        'email': shipping.email,
        'phone': shipping.phone,
        'shipping_address1': shipping.address1,
        'shipping_address2': shipping.address2,
        'city': shipping.city,
        'state': shipping.state,
        'zipcode': shipping.zipcode,
        'country': shipping.country
    }

    context = {
        'cart_items': cart_items,
        'order_total': order_total,
        'total_quantity': total_quantity,
        'shipping': request.session['shipping'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'currency': 'INR'
    }
    return render(request, 'payment/payment.html', context)

@csrf_exempt
def process_payment(request):
    cart_instance = Cart(request)
    order_total = cart_instance.order_total()

    # Create a Razorpay order
    data = {
        'amount': int(order_total * 100),  # Amount in paise
        'currency': 'INR',
        'payment_capture': '1'  # Auto-capture payment
    }
    try:
        order = razorpay_client.order.create(data=data)
    except Exception as e:
        messages.error(request, f'An error occurred while creating the payment order: {str(e)}')
        return redirect('payment')

    # Save the Razorpay order ID in the session
    request.session['razorpay_order_id'] = order['id']

    context = {
        'order_id': order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': order['amount'],
        'currency': order['currency']
    }
    return render(request, 'payment/process_payment.html', context)

@csrf_exempt
def payment_execute(request):
    if request.method == 'GET':
        payment_id = request.GET.get('razorpay_payment_id')
        order_id = request.GET.get('razorpay_order_id')
        signature = request.GET.get('razorpay_signature')

        # Verify the payment signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
        except SignatureVerificationError:
            messages.error(request, 'Payment verification failed. Please try again.')
            return redirect('payment')

        # Fetch payment details from Razorpay
        try:
            payment = razorpay_client.payment.fetch(payment_id)
            if payment['status'] == 'captured':
                # Payment successful
                cart_instance = Cart(request)
                cart_items = cart_instance.get_prods()
                cart_quantities = cart_instance.get_quants()
                order_total = cart_instance.order_total()

                user = request.user
                shipping = request.session.get('shipping')
                amount_paid = order_total
                full_name = f"{user.first_name} {user.last_name}"
                email = user.email
                shipping_address = (
                    f"{shipping['phone']} \n"
                    f"{shipping['shipping_address1']} \n"
                    f"{shipping['shipping_address2']} \n"
                    f"{shipping['city']} \n"
                    f"{shipping['state']} \n"
                    f"{shipping['zipcode']} \n"
                    f"{shipping['country']}"
                )

                # Create the order
                order = Order(
                    user=user, 
                    full_name=full_name, 
                    email=email, 
                    amount_paid=amount_paid, 
                    shipping_address=shipping_address
                )
                order.save()

                # Create OrderItems
                for item in cart_items:
                    product = Product.objects.get(id=item.id)
                    order_item = OrderItem(
                        order=order,
                        product=product,
                        user=user,
                        quantity=cart_quantities[str(item.id)],  
                        price=item.sale_price if item.is_sale else item.price
                    )
                    order_item.save()
                    
                    # Update product stock
                    product.stock_quantity -= cart_quantities[str(item.id)]
                    product.save()

                # Clear the cart
                for key in list(request.session.keys()):
                    if key == "session_key":
                        del request.session[key]

                Profile.objects.filter(user__id=request.user.id).update(old_cart="")

                messages.success(request, 'Payment successful!')
                return redirect('order_success')
            else:
                messages.error(request, f'Payment failed. Reason: {payment["error_description"]}')
                return redirect('payment')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('payment')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('payment')
    
def order_success(request):
    return render(request, 'order_success.html')

def payment_cancel(request):
    messages.warning(request, 'Payment canceled.')
    return render(request, 'payment_cancel.html')