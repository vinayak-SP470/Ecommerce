from rest_framework import serializers
from .models import (Role, CustomUser, ProductCategory, Widget, Brand, ProductBasic, Inventory,
                     CartItem, Address, WishlistItem)
from rest_framework_simplejwt.tokens import RefreshToken

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'country_code', 'profile_image',
                  'phone_number', 'password')

    def create(self, validated_data):
        validated_data['role'] = Role.objects.get_or_create(name='Customer')[0]
        password = validated_data.pop('password')
        validated_data['is_active'] = False
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'country_code', 'profile_image',
                  'phone_number')

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name']

class WidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Widget
        fields = ['id', 'name']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']

class ProductBasicSerializer(serializers.ModelSerializer):
    exchange_policy = serializers.StringRelatedField()

    class Meta:
        model = ProductBasic
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.product_title')
    product_description = serializers.CharField(source='product.product_description')
    brand_name = serializers.CharField(source='product.brand.name', allow_null=True)
    category_name = serializers.CharField(source='product.category.name', allow_null=True)
    size = serializers.StringRelatedField(source='size.name')
    color = serializers.StringRelatedField(source='color.name')

    class Meta:
        model = Inventory
        fields = ['id', 'product_title', 'brand_name', 'category_name', 'product_description',
                  'original_price', 'promo_price', 'discount', 'quantity',
                  'product_variant_description', 'size', 'color']

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields ='__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'first_name', 'last_name', 'country_code', 'phone', 'email',
                  'pin_code', 'house_flat', 'land_mark', 'area_street', 'locality_town',
                  'city_district', 'state', 'country', 'address_type', 'is_default']

class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = '__all__'

class CustomTokenObtainSerializer(serializers.Serializer):
    username_field = CustomUser.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }

        if not all(authenticate_kwargs.values()):
            raise serializers.ValidationError(
                f'Must include "{self.username_field}" and "password".',
                code='authorization_required'
            )

        user = CustomUser.objects.filter(**{self.username_field: attrs[self.username_field]}).first()

        # Check if the user exists and the password is correct
        if user and user.check_password(attrs['password']):
            # Check if the user is active
            if user.is_active:
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                return {
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'country_code': user.country_code,
                        'phone': user.phone_number,
                    },
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            else:
                # User is not active, return a message
                return {'message': 'This user is not active'}
        else:
            raise serializers.ValidationError(
                'Invalid username or password',
                code='authorization_failed'
            )


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        try:
            refresh_token = attrs['refresh']
            refresh = RefreshToken(refresh_token)
            return {
                'access': str(refresh.access_token)
            }
        except Exception as e:
            raise serializers.ValidationError('Invalid refresh token', code='invalid_refresh_token')