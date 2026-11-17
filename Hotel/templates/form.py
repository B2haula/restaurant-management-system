from django import forms

from ..models import (
    Category,
    Menu,
    MenuItem,
    OrderDetails,
    Order,
    Tablee,
    Waiter,
    WaiterTablee,
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = "__all__"


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = "__all__"


class WaiterForm(forms.ModelForm):
    class Meta:
        model = Waiter
        fields = "__all__"
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}


class TableeForm(forms.ModelForm):
    class Meta:
        model = Tablee
        fields = "__all__"


class WaiterTableeForm(forms.ModelForm):
    tablee = forms.IntegerField(
        min_value=1,
        label="Table ID",
        widget=forms.NumberInput(attrs={"placeholder": "Enter table ID"}),
    )
    waiter = forms.IntegerField(
        min_value=1,
        label="Waiter ID",
        widget=forms.NumberInput(attrs={"placeholder": "Enter waiter ID"}),
    )

    class Meta:
        model = WaiterTablee
        fields = "tablee", "waiter"

    def clean_tablee(self):
        table_id = self.cleaned_data["tablee"]
        try:
            return Tablee.objects.get(pk=table_id)
        except Tablee.DoesNotExist:
            raise forms.ValidationError("Table ID does not exist.")

    def clean_waiter(self):
        waiter_id = self.cleaned_data["waiter"]
        try:
            return Waiter.objects.get(pk=waiter_id)
        except Waiter.DoesNotExist:
            raise forms.ValidationError("Waiter ID does not exist.")


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"
        widgets = {"order_date": forms.DateInput(attrs={"type": "date"})}


class OrderDetailsForm(forms.ModelForm):
    class Meta:
        model = OrderDetails
        fields = "__all__"