from django.db import models

# Create models 

class Category(models.Model):
  category_name = models.CharField(max_length=30)

  def __str__(self):
    return self.category_name


class Menu(models.Model):
  menu_name = models.CharField(max_length=20)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  availability = models.CharField(max_length=30)
  category = models.ForeignKey(Category, on_delete=models.CASCADE)

  def __str__(self):
    return self.menu_name


class MenuItem(models.Model):
  menu_item = models.CharField(max_length=30)
  menu = models.ForeignKey(Menu, on_delete=models.CASCADE)

  def __str__(self):
    return self.menu_item


class Waiter(models.Model):
  waiter_name = models.CharField(max_length=20)
  birth_date = models.DateField()
  shift = models.CharField(max_length=30)
  contact = models.CharField(max_length=20)
  address = models.CharField(max_length=20)
  number_of_tables_assigned = models.IntegerField(null=True, blank=True)

  def __str__(self):
    return self.waiter_name


class Tablee(models.Model):
  location = models.CharField(max_length=30)
  tablee_status = models.CharField(max_length=30)
  capacity = models.CharField(max_length=10)

  def __str__(self):
    return f"Table at {self.location}"


class WaiterTablee(models.Model):
  tablee = models.ForeignKey(Tablee, on_delete=models.CASCADE)
  waiter = models.ForeignKey(Waiter, on_delete=models.CASCADE)

  @property
  def waitertablee_id(self):
    return self.pk


class Order(models.Model):
  order_type = models.CharField(max_length=30)
  customer = models.CharField(max_length=20)
  order_status = models.CharField(max_length=30)
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True)
  order_date = models.DateField()

  def __str__(self):
    return f"Order for {self.customer}"


class OrderDetails(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE)
  quantity = models.CharField(max_length=20)

  @property
  def orderdetails_id(self):
    return self.pk    