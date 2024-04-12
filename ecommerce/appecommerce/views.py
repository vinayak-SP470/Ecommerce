import random
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from rest_framework.authtoken.models import Token
from twilio.rest import Client
from .models import (ProductCategory, Widget, Brand, Variant, VariantValue, ProductBasic, Inventory,
                     CartItem, Cart, Address, CustomUser, Wishlist, WishlistItem)
from .serializers import (CustomUserSerializer, UserDetailsSerializer, ProductCategorySerializer,
                          WidgetSerializer, BrandSerializer, ProductBasicSerializer, InventorySerializer,
                          CartItemSerializer, AddressSerializer, WishlistItemSerializer)
from .renderers import BrandJSONRenderer, CustomerProfileRenderer

# Function to generate random number for otp (Twilio)
def generate_otp(length=6):
    return ''.join(random.choices('0123456789', k=length))

# Customer
# Add a new customer(sign-up)
@swagger_auto_schema(
    method='post',
    security=[],
    operation_description="Create a new customer",
    request_body=openapi.Schema(
        type='object',
        properties={
            'username': openapi.Schema(type='string', description='Username of the customer'),
            'first_name': openapi.Schema(type='string', description='First name of the customer'),
            'last_name': openapi.Schema(type='string', description='Last name of the customer'),
            'email': openapi.Schema(type='string', format='email',
                                    description='Email address of the customer'),
            'country_code': openapi.Schema(type='string',
                                           description='Country code of the customer\'s phone number'),
            'phone_number': openapi.Schema(type='string', description='Phone number of the customer'),
            'profile_image': openapi.Schema(type='string', format='binary',
                                            description='Profile image of the customer (binary data)'),
            'password': openapi.Schema(type='string', description='Password of the customer'),
        }
    ),    responses={
        status.HTTP_201_CREATED: 'Customer created successfully',
        status.HTTP_400_BAD_REQUEST: 'Bad request',
    }
)
@api_view(['POST'])
def create_customer(request):
    if request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            otp = generate_otp()
            user.otp = otp
            user.token = token.key
            user.save()
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = f'Your OTP is: {otp}'
            client.messages.create(to=request.data['country_code'] + request.data['phone_number'],
                                   from_='+13346030803',
                                   body=message)

            response_data = serializer.data
            response_data['token'] = token.key
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Verify the user for sign-up with otp and token
@swagger_auto_schema(
    method='post',
    security=[],
    operation_description="Verify OTP and activate user",
    request_body=openapi.Schema(
        type='object',
        properties={
            'otp': openapi.Schema(type='string', description='OTP received by the user'),
            'token': openapi.Schema(type='string', description='Token associated with the user'),
        }
    ),
    responses={
        status.HTTP_200_OK: 'User activated successfully',
        status.HTTP_400_BAD_REQUEST: 'Bad request',
    }
)
@api_view(['POST'])
def verify_otp(request):
    if request.method == 'POST':
        otp = request.data.get('otp')
        token = request.data.get('token')
        if not otp or not token:
            return Response({'message': 'Both OTP and token are required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.get(token=token)
        except CustomUser.DoesNotExist:
            return Response({'message': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.otp != otp:
            return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        return Response({'message': 'User activated successfully.'}, status=status.HTTP_200_OK)

# Function to fetch customer profile details
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@renderer_classes([CustomerProfileRenderer])
def customer_profile(request):
    user = request.user
    serializer = UserDetailsSerializer(user)
    return Response(serializer.data)

# Product
# Function to fetch product categories
@swagger_auto_schema(method='get', security=[])
@api_view(['GET'])
def product_category_list(request):
    categories = ProductCategory.objects.all()
    serializer = ProductCategorySerializer(categories, many=True)
    return Response(serializer.data)

# Function to fetch product widgets
@swagger_auto_schema(method='get', security=[])
@api_view(['GET'])
def widget_list(request):
    widgets = Widget.objects.all()
    serializer = WidgetSerializer(widgets, many=True)
    return Response(serializer.data)

# Function to fetch product brand lists
@swagger_auto_schema(method='get', security=[])
@api_view(['GET'])
@renderer_classes([BrandJSONRenderer])
def brand_list(request):
    brands = Brand.objects.all()
    serializer = BrandSerializer(brands, many=True)
    return Response(serializer.data)

# Function to fetch different product variants
@swagger_auto_schema(method='get', security=[])
@api_view(['GET'])
def variant_list(request):
    variants = Variant.objects.all()
    data = []
    for variant in variants:
        variant_data = {
            "id": variant.id,
            "name": variant.name,
            "childVariants": []
        }
        values = VariantValue.objects.filter(variant=variant)
        for value in values:
            value_data = {
                "id": value.id,
                "name": value.name,
                "parentID": value.variant_id,
                # "sort_order": value.sort_order
            }
            variant_data["childVariants"].append(value_data)
        data.append(variant_data)

    return Response(data)

# Function to fetch basic product details by passing product ID

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_detail(request, product_id):
    if request.method == 'GET':
        if not product_id:
            return Response({"message": "Product ID is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            product = ProductBasic.objects.get(pk=product_id)
            serializer = ProductBasicSerializer(product)
            return Response(serializer.data)
        except ProductBasic.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

# Function to fetch inventory details of products by passing inventory ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_detail(request, inventory_id):
    if request.method == 'GET':
        if not inventory_id:
            return Response({"message": "Inventory ID is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            inventory = Inventory.objects.get(pk=inventory_id)
            serializer = InventorySerializer(inventory)
            return Response(serializer.data)
        except Inventory.DoesNotExist:
            return Response({"message": "Inventory not found"}, status=status.HTTP_404_NOT_FOUND)

# Cart
# Function to fetch cart details of customer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_list(request):
    try:
        customer_cart = Cart.objects.get(customer=request.user)
        cart_items = CartItem.objects.filter(cart=customer_cart)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response({'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

# Function to add cart item to logged in customer
@swagger_auto_schema(
    method='post',
    operation_description="Add item(s) to cart",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['product_id', 'quantity'],
        properties={
            'product_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                         description='ID of the product to add to cart'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER,
                                       description='Quantity of the product to add to cart'),
        },
    ),
    responses={
        status.HTTP_201_CREATED: 'Item(s) added to cart successfully',
        status.HTTP_400_BAD_REQUEST: 'Bad request (e.g., missing required fields)',
        status.HTTP_401_UNAUTHORIZED: 'Unauthorized: Authentication credentials were not provided',
        status.HTTP_404_NOT_FOUND: 'Product not found',
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')

    if not product_id or not quantity:
        return Response({'error': 'Product ID and quantity are required'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        product = Inventory.objects.get(pk=product_id)
    except Inventory.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        customer_cart = Cart.objects.get(customer=request.user)
    except Cart.DoesNotExist:
        customer_cart = Cart.objects.create(customer=request.user)

    try:
        cart_item = CartItem.objects.get(cart=customer_cart, inventory=product)
        cart_item.quantity += int(quantity)
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(cart=customer_cart, inventory=product, quantity=int(quantity))

    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# Function to delete cart item by passing cart item ID
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(pk=cart_item_id)
        cart_item.delete()
        return Response({'message': 'Cart item deleted successfully'},
                        status=status.HTTP_204_NO_CONTENT)
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

# Function to update cart item quantity by passing cart item ID and quantity
@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['cartId', 'quantity'],
        properties={
            'cartId': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the cart item'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER,
                                       description='New quantity of the cart item'),
        },
    ),
    responses={
        status.HTTP_200_OK: 'Cart item quantity updated successfully',
        status.HTTP_400_BAD_REQUEST: 'Bad request (e.g., missing cartId or quantity)',
        status.HTTP_404_NOT_FOUND: 'Cart item not found',
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item_quantity(request):
    data = request.data
    cart_id = data.get('cartId')
    quantity = data.get('quantity')
    if cart_id is None or quantity is None:
        return Response({'error': 'cartId and quantity are required'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        cart_item = CartItem.objects.get(pk=cart_id)
        cart_item.quantity = quantity
        cart_item.save()
        return Response({'message': 'Cart item quantity updated successfully'},
                        status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

# Function to delete entire cart item by passing cart ID of logged in customer if exist
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_customer_cart_items(request):
    try:
        customer_cart = Cart.objects.get(customer=request.user)
        customer_cart.cartitem_set.all().delete()
        customer_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Cart.DoesNotExist:
        return Response({'error': 'Customer cart does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'An error occurred while deleting customer cart items'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Address
# Function to fetch all address of the logged in customer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def address_list(request):
    addresses = Address.objects.filter(customer=request.user)
    if addresses.exists():
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)
    else:
        return Response({"message": "No addresses exist."}, status=status.HTTP_404_NOT_FOUND)

# Function to add address
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['first_name', 'last_name', 'country_code', 'phone', 'email', 'pin_code',
                  'house_flat', 'address_type', 'is_default'],
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
            'country_code': openapi.Schema(type=openapi.TYPE_STRING, description='Country code'),
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
            'pin_code': openapi.Schema(type=openapi.TYPE_STRING, description='PIN code'),
            'house_flat': openapi.Schema(type=openapi.TYPE_STRING, description='House/Flat number'),
            'land_mark': openapi.Schema(type=openapi.TYPE_STRING, description='Landmark'),
            'area_street': openapi.Schema(type=openapi.TYPE_STRING, description='Area/Street'),
            'locality_town': openapi.Schema(type=openapi.TYPE_STRING, description='Locality/Town'),
            'city_district': openapi.Schema(type=openapi.TYPE_STRING, description='City/District'),
            'state': openapi.Schema(type=openapi.TYPE_STRING, description='State'),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description='Country'),
            'address_type': openapi.Schema(type=openapi.TYPE_STRING, description='Address type'),
            'is_default': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Is default address')
        },
    ),
    responses={
        status.HTTP_201_CREATED: 'Address created successfully',
        status.HTTP_400_BAD_REQUEST: 'Bad request (e.g., missing required fields)',
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_address(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['customer_id'] = request.user.id
        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Function to fetch one address by passing the address ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_address_by_id(request, address_id):
    try:
        address = Address.objects.get(id=address_id, customer=request.user)
        serializer = AddressSerializer(address)
        return Response(serializer.data)
    except Address.DoesNotExist:
        return Response({"message": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

# Function to edit the address by passing address ID
@swagger_auto_schema(
    method='patch',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'first_name': {'type': 'string', 'description': 'First name'},
            'last_name': {'type': 'string', 'description': 'Last name'},
            'country_code': {'type': 'string', 'description': 'Country code'},
            'phone': {'type': 'string', 'description': 'Phone number'},
            'email': {'type': 'string', 'description': 'Email address'},
            'pin_code': {'type': 'string', 'description': 'PIN code'},
            'house_flat': {'type': 'string', 'description': 'House/Flat number'},
            'land_mark': {'type': 'string', 'description': 'Landmark'},
            'area_street': {'type': 'string', 'description': 'Area/Street'},
            'locality_town': {'type': 'string', 'description': 'Locality/Town'},
            'city_district': {'type': 'string', 'description': 'City/District'},
            'state': {'type': 'string', 'description': 'State'},
            'country': {'type': 'string', 'description': 'Country'},
            'address_type': {'type': 'string', 'description': 'Address type'},
            'is_default': {'type': 'boolean', 'description': 'Is default address'}
        },
        required=['first_name', 'last_name', 'country_code', 'phone', 'email', 'pin_code',
                  'house_flat', 'land_mark', 'area_street', 'locality_town', 'city_district', 'state',
                  'country', 'address_type', 'is_default']
    ),
    responses={
        200: 'Address details updated successfully',
        400: 'Bad request',
        404: 'Address not found'
    }
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_address(request, address_id):
    try:
        address = Address.objects.get(id=address_id, customer=request.user)
    except Address.DoesNotExist:
        return Response({"message": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = AddressSerializer(address, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Address details updated successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Function to delete address by passing address ID
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_address(request, address_id):
    try:
        address = Address.objects.get(id=address_id, customer=request.user)
    except Address.DoesNotExist:
        return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

    address.delete()
    return Response({"message": "Address deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_default_address(request):
    user = request.user
    try:
        default_address = Address.objects.get(customer=user, is_default=True)
        serializer = AddressSerializer(default_address)
        return Response(serializer.data)
    except Address.DoesNotExist:
        return Response({'message': 'Default address not found.'}, status=404)

# Wishlish

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_wishlist(request):
    user = request.user
    wishlist_items = WishlistItem.objects.filter(wishlist__user=user)
    serializer = WishlistItemSerializer(wishlist_items, many=True)
    return Response(serializer.data)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request, inventory_id):
    if request.method == 'POST':
        if not inventory_id:
            return Response({'message': 'Inventory ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            inventory = Inventory.objects.get(id=inventory_id)
        except Inventory.DoesNotExist:
            return Response({'message': 'Inventory not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        # Create or get the user's wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=user)

        # Check if the item is already in the wishlist
        if wishlist.items.filter(inventory=inventory).exists():
            return Response({'message': 'Item already in wishlist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Add item to wishlist
        wishlist_item = WishlistItem.objects.create(wishlist=wishlist, inventory=inventory)
        wishlist_item_serializer = WishlistItemSerializer(wishlist_item)

        # Update is_wishlisted field of inventory
        inventory.is_wishlisted = True
        inventory.save()

        return Response({'message': 'Item added to wishlist successfully.'}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_wishlist(request, wishlist_item_id):
    user = request.user

    try:
        wishlist_item = WishlistItem.objects.get(id=wishlist_item_id, wishlist__user=user)
    except WishlistItem.DoesNotExist:
        return Response({'message': 'Wishlist item not found.'}, status=404)
    inventory = wishlist_item.inventory
    inventory.is_wishlisted = False
    inventory.save()
    wishlist_item.delete()
    return Response({'message': 'Item removed from wishlist successfully.'}, status=200)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_wishlist(request):
    user = request.user
    wishlist_items = WishlistItem.objects.filter(wishlist__user=user)
    for wishlist_item in wishlist_items:
        inventory = wishlist_item.inventory
        inventory.is_wishlisted = False
        inventory.save()
        wishlist_item.delete()
    return Response({'message': 'Wishlist cleared successfully.'}, status=200)


# # Function to log in (access token)
# @swagger_auto_schema(method='post', security=[], request_body=openapi.Schema(type=openapi.TYPE_OBJECT), responses={200: 'Success'})
# @api_view(['POST'])
# @authentication_classes([])
# @permission_classes([])
# def custom_token_obtain_pair(request):
#     return TokenObtainPairView.as_view()(request)
#
# # Function for refresh token
# @swagger_auto_schema(method='post', security=[], request_body=openapi.Schema(type=openapi.TYPE_OBJECT), responses={200: 'Success'})
# @api_view(['POST'])
# @authentication_classes([])
# @permission_classes([])
# def custom_token_refresh(request):
#     return TokenRefreshView.as_view()(request)

