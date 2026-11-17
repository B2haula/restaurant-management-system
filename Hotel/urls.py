from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views
from .forms import KaiadminAuthenticationForm

app_name = "restaurant"

urlpatterns = [
    path("login/", LoginView.as_view(
        template_name="login.html",
        authentication_form=KaiadminAuthenticationForm,
    ), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", views.index_page, name="index"),
    path("about/", views.about_page, name="about"),
    path("categories/", views.category_page, name="category"),
    path("menus/", views.menu_page, name="menu"),
    path("menu-items/", views.menuitem_page, name="menuitem"),
    path("waiters/", views.waiter_page, name="waiter"),
    path("tables/", views.table_page, name="table"),
    path("waiter-tables/", views.waitertablee_page, name="waitertablee"),
    path("orders/", views.order_page, name="order"),
    path("order-details/", views.order_details_page, name="order_details"),
]
