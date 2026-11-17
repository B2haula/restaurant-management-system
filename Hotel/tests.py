from django import forms
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse

from .models import Category, Menu, Order, Tablee, Waiter, WaiterTablee


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="staff", password="secure-pass-123")

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("restaurant:category"))
        self.assertRedirects(response, "/login/?next=/categories/")

    def test_valid_login_redirects_to_restaurant(self):
        response = self.client.post(reverse("restaurant:login"), {
            "username": "staff",
            "password": "secure-pass-123",
        })
        self.assertRedirects(response, reverse("restaurant:index"))

    def test_login_page_displays_delizio_branding(self):
        response = self.client.get(reverse("restaurant:login"))
        self.assertContains(response, 'alt="Delizio Culinary Elegance"')
        self.assertContains(response, "Delizio Restaurant")
        self.assertContains(response, "Restaurant Management System")
        self.assertContains(response, "Sign in to your account")
        self.assertContains(response, "Secure access for Delizio Restaurant staff.")

    def test_logout_redirects_to_login(self):
        self.client.login(username="staff", password="secure-pass-123")
        response = self.client.post(reverse("restaurant:logout"))
        self.assertRedirects(response, reverse("restaurant:login"))

    def test_protected_page_is_accessible_after_login(self):
        self.client.login(username="staff", password="secure-pass-123")
        Category.objects.create(category_name="Meals")
        response = self.client.get(reverse("restaurant:category"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add New Category")
        self.assertContains(response, "table-head-bg-primary")
        self.assertContains(response, 'class="sidebar-account"')
        self.assertContains(response, "fas fa-table")
        self.assertContains(response, 'action="/logout/"')
        self.assertContains(response, "Signed in")
        self.assertContains(response, 'stroke="currentColor"')
        self.assertContains(response, 'aria-label="Edit record"')
        self.assertContains(response, 'aria-label="Delete record"')

        edit_response = self.client.get(f"{reverse('restaurant:category')}?edit={Category.objects.get(category_name='Meals').pk}")
        self.assertContains(edit_response, "Add New Category")
        self.assertContains(edit_response, f"{reverse('restaurant:category')}?new=1")

        new_record_response = self.client.get(f"{reverse('restaurant:category')}?new=1")
        self.assertContains(new_record_response, 'class="modal fade show"')
        self.assertContains(new_record_response, "backdrop-filter: blur(8px)")
        self.assertContains(new_record_response, 'aria-hidden="false"')
        self.assertContains(new_record_response, 'class="modal-backdrop fade show"')

    def test_about_page_requires_login(self):
        response = self.client.get(reverse("restaurant:about"))
        self.assertRedirects(response, "/login/?next=/about/")


class AboutPageTests(TestCase):
    def test_about_page_has_welcome_contact_and_navigation_link(self):
        User.objects.create_user(username="staff", password="secure-pass-123")
        self.client.login(username="staff", password="secure-pass-123")

        response = self.client.get(reverse("restaurant:about"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Delizio Restaurant")
        self.assertContains(response, "menu categories, prices and availability")
        self.assertContains(response, "today's sales from confirmed orders")
        self.assertContains(response, "waiter-to-table assignments")
        self.assertNotContains(response, "A better way to run your restaurant")
        self.assertContains(response, "hello@tableandthyme.example")
        self.assertContains(response, "+1 (555) 010-2040")
        self.assertContains(response, f'href="{reverse("restaurant:about")}"')
        self.assertContains(response, 'alt="Delizio Culinary Elegance"')
        self.assertContains(response, "Delizio Restaurant Management System")


class DashboardTests(TestCase):
    def setUp(self):
        User.objects.create_user(username="staff", password="secure-pass-123")
        self.client.login(username="staff", password="secure-pass-123")
        self.category = Category.objects.create(category_name="Meals")
        self.menu = Menu.objects.create(
            menu_name="Lunch",
            price=Decimal("12.50"),
            availability="yes",
            category=self.category,
        )

    def test_dashboard_uses_confirmed_orders_for_sales_and_payment_history(self):
        today = date.today()
        Order.objects.create(
            order_type="Dine-in", customer="Ada", order_status="confirmed",
            amount=Decimal("25.00"), menu=self.menu, order_date=today,
        )
        Order.objects.create(
            order_type="Takeaway", customer="Lin", order_status="pending",
            amount=Decimal("80.00"), menu=self.menu, order_date=today,
        )

        response = self.client.get(reverse("restaurant:index"))

        self.assertContains(response, 'href="/categories/" class="card card-stats card-round text-decoration-none"')
        self.assertContains(response, 'href="/menus/" class="card card-stats card-round text-decoration-none"')
        self.assertContains(response, 'href="/waiters/" class="card card-stats card-round text-decoration-none"')
        self.assertContains(response, 'href="/orders/" class="card card-stats card-round text-decoration-none"')
        self.assertContains(response, f'href="{reverse("restaurant:about")}"')
        self.assertContains(response, "Welcome to Delizio Restaurant")
        self.assertContains(response, "menu categories, prices and availability")
        self.assertContains(response, "fas fa-table")
        self.assertContains(response, 'alt="Delizio Culinary Elegance"')
        self.assertContains(response, "table-head-bg-primary")
        self.assertContains(response, "staff")
        self.assertContains(response, "Logout")
        self.assertEqual(response.context["daily_sales"], Decimal("25.00"))
        self.assertEqual(response.context["confirmed_order_count"], 1)
        self.assertEqual(list(response.context["payment_history"].values_list("customer", flat=True)), ["Ada"])
        response_html = response.content.decode("utf-8")
        self.assertTrue("Payment History" in response_html, "payment history section is missing")
        self.assertTrue("Order #1" in response_html, "confirmed order is missing from history")
        history_column_positions = [
            response_html.index("<th scope=\"col\">Customer</th>", response_html.index("Payment History")),
            response_html.index("<th scope=\"col\">Menu ID</th>", response_html.index("Payment History")),
        ]
        self.assertEqual(history_column_positions, sorted(history_column_positions))
        self.assertContains(response, f"<td>{self.menu.pk}</td>")
        self.assertFalse("New Customers" in response_html, "sample customer panel is present")
        self.assertFalse("Users Geolocation" in response_html, "sample geolocation panel is present")
        self.assertFalse("User Statistics" in response_html, "empty sample statistics panel is present")
        self.assertFalse("Search ..." in response_html, "dashboard search control is present")
        self.assertFalse("dropdownMenuButton" in response_html, "placeholder export menu is present")
        self.assertFalse("messageDropdown" in response_html, "demo messages control is present")
        self.assertFalse("notifDropdown" in response_html, "demo notifications control is present")
        self.assertFalse("ThemeKita" in response_html, "template vendor footer is present")
        self.assertFalse("ThemeWagon" in response_html, "template distributor footer is present")
        self.assertTrue("Delizio Restaurant Management System" in response_html, "restaurant footer is missing")

    def test_orders_page_uses_numeric_menu_id_after_customer(self):
        response = self.client.get(reverse("restaurant:order"))

        form_labels = [field.label for field in response.context["form"]]
        column_labels = [heading for heading, _ in response.context["columns"]]

        self.assertEqual(form_labels.index("Menu ID"), form_labels.index("Customer") + 1)
        self.assertEqual(column_labels.index("Menu ID"), column_labels.index("Customer") + 1)
        self.assertIsInstance(response.context["form"].fields["menu"].widget, forms.NumberInput)
        self.assertContains(response, 'type="number"')
        self.assertNotContains(response, "<select")

    def test_order_accepts_existing_menu_id_and_rejects_unknown_id(self):
        response = self.client.post(reverse("restaurant:order"), {
            "order_type": "Dine-in",
            "customer": "Ada",
            "menu": str(self.menu.pk),
            "order_status": "pending",
            "amount": "12.50",
            "order_date": date.today().isoformat(),
        })

        self.assertRedirects(response, f"{reverse('restaurant:order')}?saved=1")
        self.assertEqual(Order.objects.get(customer="Ada").menu_id, self.menu.pk)

        response = self.client.post(reverse("restaurant:order"), {
            "order_type": "Dine-in",
            "customer": "Lin",
            "menu": "999999",
            "order_status": "pending",
            "amount": "12.50",
            "order_date": date.today().isoformat(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "menu", "Enter an existing Menu ID.")

    def test_dashboard_lists_waiter_table_ids_in_requested_order(self):
        waiter = Waiter.objects.create(
            waiter_name="Mina",
            birth_date=date(2000, 1, 1),
            shift="day",
            contact="555-0100",
            address="Main Street",
        )
        table = Tablee.objects.create(
            location="window",
            tablee_status="occupied",
            capacity="4",
        )
        assignment = WaiterTablee.objects.create(waiter=waiter, tablee=table)

        response = self.client.get(reverse("restaurant:index"))
        response_html = response.content.decode("utf-8")
        column_positions = [
            response_html.index("WaiterTablee ID"),
            response_html.index("Waiter ID"),
            response_html.index("Table ID"),
        ]

        self.assertEqual(column_positions, sorted(column_positions))
        self.assertContains(response, f"<td>{assignment.waitertablee_id}</td>")
        self.assertContains(response, f"<td>{waiter.pk}</td>")
        self.assertContains(response, f"<td>{table.pk}</td>")

    def test_waitertablee_form_selects_existing_waiter_and_table(self):
        waiter = Waiter.objects.create(
            waiter_name="Mina",
            birth_date=date(2000, 1, 1),
            shift="day",
            contact="555-0100",
            address="Main Street",
        )
        table = Tablee.objects.create(
            location="window",
            tablee_status="occupied",
            capacity="4",
        )

        response = self.client.get(reverse("restaurant:waitertablee"))
        form = response.context["form"]
        self.assertEqual(list(form.fields), ["waiter", "tablee"])
        self.assertEqual(form.fields["waiter"].label_from_instance(waiter), f"{waiter.pk} - Mina")
        self.assertEqual(form.fields["tablee"].label_from_instance(table), f"{table.pk} - Window table")

        response = self.client.post(reverse("restaurant:waitertablee"), {
            "waiter": waiter.pk,
            "tablee": table.pk,
        })

        self.assertRedirects(response, f"{reverse('restaurant:waitertablee')}?saved=1")
        self.assertTrue(WaiterTablee.objects.filter(waiter=waiter, tablee=table).exists())

    def test_waiter_record_displays_its_actual_id_used_by_waiter_tablee(self):
        waiter = Waiter.objects.create(
            id=7,
            waiter_name="Mina",
            birth_date=date(2000, 1, 1),
            shift="day",
            contact="555-0100",
            address="Main Street",
        )

        waiter_response = self.client.get(reverse("restaurant:waiter"))
        waitertablee_response = self.client.get(reverse("restaurant:waitertablee"))

        self.assertRegex(waiter_response.content.decode(), r"<td>\s*7\s*</td>")
        self.assertContains(waitertablee_response, f"{waiter.pk} - Mina")
