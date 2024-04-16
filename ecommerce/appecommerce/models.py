from django.db import models
from django.contrib.auth.models import AbstractUser
import stripe
# Model class for different roles
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

# Model class for different user
class CustomUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    country_code = models.CharField(max_length=10, blank=True)
    profile_image = models.BinaryField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    groups = models.ManyToManyField("auth.Group", related_name="custom_users", blank=True)
    user_permissions = models.ManyToManyField("auth.Permission", related_name="custom_users", blank=True)
    otp = models.CharField(max_length=6, blank=True)
    token = models.CharField(max_length=100, blank=True)
    stripe_id = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.stripe_id and self.email:  # Ensure email is not empty
            try:
                stripe_customer = stripe.Customer.create(email=self.email)
                self.stripe_id = stripe_customer.id
            except stripe.error.StripeError as e:
                pass  # You can add your error handling logic here

        super().save(*args, **kwargs)

# Model class for different category in products like fashion, electronics
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model class for different widget in products like Best selling, trending
class Widget(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model class for different brands in products like Dell, JBL, One plus
class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model class for different variants in products like color, size, RAM
class Variant(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model class for different variants in products like color, size, RAM
class VariantValue(models.Model):
    name = models.CharField(max_length=100)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='values')
    # sort_order = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

# Model class for different exchange policy
class ExchangePolicy(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model class for basic product details
class ProductBasic(models.Model):
    product_title = models.CharField(max_length=255)
    product_description = models.TextField()
    exchange_policy = models.ForeignKey(ExchangePolicy, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products', blank=True, null=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=True, null=True)
    widget = models.ForeignKey(Widget, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.brand:
            return f"{self.product_title} ({self.brand.name})"
        else:
            return self.product_title
# Model class for inventory details
class Inventory(models.Model):
    product = models.ForeignKey(ProductBasic, on_delete=models.CASCADE)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    promo_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    product_variant_description = models.CharField(max_length=255, blank=True)
    is_wishlisted = models.BooleanField(default=False)
    stock_status = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        if self.quantity > 0:
            self.stock_status = "Have stock"
        else:
            self.stock_status = "Out of stock"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product.product_title
    @classmethod
    def add_variant_fields(cls):
        variants = Variant.objects.all()
        for variant in variants:
            field_name = variant.name.lower().replace(' ', '_')
            field = models.ForeignKey(VariantValue, on_delete=models.CASCADE, related_name=f'{field_name}s', null=True,
                                      blank=True)
            cls.add_to_class(field_name, field)

    def __str__(self):
        return self.product.product_title

Inventory.add_variant_fields()

# Model class for cart for all customers
class Cart(models.Model):
    customer = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.customer.username}"

# Model class for cart items
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.inventory.product.product_title} - Quantity: {self.quantity}"

# Model class for address details
class Address(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ('HOME', 'Home'),
        ('WORK', 'Work'),
        ('OTHER', 'Other'),
    )
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=3)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    pin_code = models.CharField(max_length=10)
    house_flat = models.CharField(max_length=100)
    land_mark = models.CharField(max_length=100)
    area_street = models.CharField(max_length=100)
    locality_town = models.CharField(max_length=100)
    city_district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(customer=self.customer).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Wishlist of {self.user.username}"

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inventory.product.product_title} - {self.added_at}"

class PaymentCard(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()
    cvc = models.CharField(max_length=3)
    brand = models.CharField(max_length=50, blank=True)
    stripe_card_id = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user}-brand{self.brand} ending in {self.card_number[-4:]}"