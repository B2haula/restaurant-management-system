from django import forms
from django.contrib.auth.forms import AuthenticationForm

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


class KaiadminModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            control_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs["class"] = control_class


class KaiadminAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class CategoryForm(KaiadminModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class MenuForm(KaiadminModelForm):
    class Meta:
        model = Menu
        fields = "__all__"


class MenuItemForm(KaiadminModelForm):
    class Meta:
        model = MenuItem
        fields = "__all__"


class WaiterForm(KaiadminModelForm):
    class Meta:
        model = Waiter
        fields = "__all__"
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}


class TableeForm(KaiadminModelForm):
    class Meta:
        model = Tablee
        fields = "__all__"


class WaiterIdChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.pk} - {obj.waiter_name}"


class TableIdChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.pk} - {obj.location.title()} table"


class WaiterTableeForm(KaiadminModelForm):
    waiter = WaiterIdChoiceField(
        queryset=Waiter.objects.order_by("pk"),
        label="Waiter ID",
        empty_label="Select a waiter",
    )
    tablee = TableIdChoiceField(
        queryset=Tablee.objects.order_by("pk"),
        label="Table ID",
        empty_label="Select a table",
    )

    class Meta:
        model = WaiterTablee
        fields = "waiter", "tablee"


class OrderForm(KaiadminModelForm):
    menu = forms.IntegerField(
        label="Menu ID",
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={"min": 1}),
    )

    class Meta:
        model = Order
        fields = ("order_type", "customer", "menu", "order_status", "amount", "order_date")
        widgets = {"order_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and self.instance and self.instance.menu_id:
            self.initial["menu"] = self.instance.menu_id

    def clean_menu(self):
        menu_id = self.cleaned_data["menu"]
        if menu_id is None:
            return None

        try:
            return Menu.objects.get(pk=menu_id)
        except Menu.DoesNotExist:
            raise forms.ValidationError("Enter an existing Menu ID.")


class OrderDetailsForm(KaiadminModelForm):
    class Meta:
        model = OrderDetails
        fields = "__all__"
