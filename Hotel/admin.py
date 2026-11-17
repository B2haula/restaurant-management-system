from django.contrib import admin
from .models import (
    Category,
    Menu,
    MenuItem,
    OrderDetails,
    Order,
    Tablee,
    Waiter,
    WaiterTablee,
)


admin.site.register(Category)
admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderDetails)
admin.site.register(Tablee)
admin.site.register(Waiter)
admin.site.register(WaiterTablee)
