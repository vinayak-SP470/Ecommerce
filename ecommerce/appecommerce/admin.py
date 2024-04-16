from django.contrib import admin
from .models import (Role, CustomUser, Brand, Widget, ProductCategory, Variant,
                     VariantValue, ExchangePolicy, ProductBasic, Inventory, CartItem, Cart, Address, PaymentCard)

admin.site.register(Role)
admin.site.register(CustomUser)
admin.site.register(ProductCategory)
admin.site.register(Widget)
admin.site.register(Brand)
admin.site.register(Variant)
admin.site.register(VariantValue)
admin.site.register(ExchangePolicy)
admin.site.register(ProductBasic)
admin.site.register(Inventory)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Address)
admin.site.register(PaymentCard)



