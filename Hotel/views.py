from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    CategoryForm,
    MenuForm,
    MenuItemForm,
    OrderDetailsForm,
    OrderForm,
    TableeForm,
    WaiterForm,
    WaiterTableeForm,
)
from .models import (
    Category,
    Menu,
    MenuItem,
    Order,
    OrderDetails,
    Tablee,
    Waiter,
    WaiterTablee,
)

ADD_BUTTON_LABELS = {
    "Categories": "Add New Category",
    "Menus": "Add New Menu",
    "Menu Items": "Add New Menu Item",
    "Waiters": "Add New Waiter",
    "Tables": "Add New Table",
    "WaiterTablee": "Add New Waiter Table",
    "Orders": "Add New Order",
    "Order Details": "Add New Order Detail",
}


def _crud(request, model, form_class, url_name, title, columns, template_name="records.html"):
    edit_id = request.POST.get("edit_id") or request.GET.get("edit")
    instance = get_object_or_404(model, pk=edit_id) if edit_id else None

    if request.method == "POST":
        if request.POST.get("delete_id"):
            model.objects.filter(pk=request.POST["delete_id"]).delete()
            return redirect(url_name)
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(f"{request.path}?saved=1")
    else:
        form = form_class(instance=instance)

    return render(request, template_name, {
        "title": title,
        "add_button_label": ADD_BUTTON_LABELS[title],
        "form": form,
        "objects": model.objects.all(),
        "columns": columns,
        "editing": instance is not None,
    })


@login_required
def index_page(request):
    today = timezone.localdate()
    confirmed_orders = Order.objects.filter(order_status="confirmed").order_by("-order_date", "-pk")
    todays_confirmed_orders = confirmed_orders.filter(order_date=today)
    return render(request, "dashboard.html", {
        "category_count": Category.objects.count(),
        "menu_count": Menu.objects.count(),
        "menu_item_count": MenuItem.objects.count(),
        "waiter_count": Waiter.objects.count(),
        "table_count": Tablee.objects.count(),
        "waiter_table_count": WaiterTablee.objects.count(),
        "waiter_table_records": WaiterTablee.objects.select_related(
            "waiter", "tablee"
        ).order_by("pk"),
        "order_count": Order.objects.count(),
        "order_detail_count": OrderDetails.objects.count(),
        "daily_sales": todays_confirmed_orders.aggregate(total=Sum("amount"))["total"] or 0,
        "confirmed_order_count": todays_confirmed_orders.count(),
        "payment_history": confirmed_orders,
        "today": today,
    })


@login_required
def about_page(request):
    return render(request, "about.html")


@login_required
def category_page(request):
    return _crud(request, Category, CategoryForm, "restaurant:category",
                 "Categories", [("ID", "id"), ("Name", "category_name")])


@login_required
def menu_page(request):
    return _crud(request, Menu, MenuForm, "restaurant:menu",
                 "Menus", [
                     ("ID", "id"), ("Name", "menu_name"), ("Price", "price"),
                     ("Availability", "availability"), ("Category", "category"),
                 ])


@login_required
def menuitem_page(request):
    return _crud(request, MenuItem, MenuItemForm, "restaurant:menuitem",
                 "Menu Items", [
                     ("Menu Item ID", "id"),
                     ("Name", "menu_item"),
                     ("Menu ID", "menu_id"),
                 ])


@login_required
def waiter_page(request):
    return _crud(request, Waiter, WaiterForm, "restaurant:waiter",
                 "Waiters", [
                     ("ID", "id"), ("Name", "waiter_name"),
                     ("Birth date", "birth_date"), ("Shift", "shift"),
                     ("Contact", "contact"), ("Address", "address"),
                     ("Tables assigned", "number_of_tables_assigned"),
                 ])


@login_required
def table_page(request):
    return _crud(request, Tablee, TableeForm, "restaurant:table",
                 "Tables", [
                     ("ID", "id"), ("Location", "location"),
                     ("Status", "tablee_status"), ("Capacity", "capacity"),
                 ])


@login_required
def waitertablee_page(request):
    return _crud(request, WaiterTablee, WaiterTableeForm, "restaurant:waitertablee",
                 "WaiterTablee", [
                     ("WaiterTablee ID", "waitertablee_id"),
                     ("Waiter ID", "waiter_id"),
                     ("Table ID", "tablee_id"),
                 ])


@login_required
def order_page(request):
    return _crud(request, Order, OrderForm, "restaurant:order",
                 "Orders", [
                     ("ID", "id"), ("Type", "order_type"), ("Customer", "customer"),
                     ("Menu ID", "menu_id"),
                     ("Status", "order_status"), ("Amount", "amount"),
                     ("Date", "order_date"),
                 ])


@login_required
def order_details_page(request):
    return _crud(request, OrderDetails, OrderDetailsForm, "restaurant:order_details",
                 "Order Details", [
                     ("Order Details ID", "orderdetails_id"),
                     ("Order", "order"),
                     ("Quantity", "quantity"),
                 ])
