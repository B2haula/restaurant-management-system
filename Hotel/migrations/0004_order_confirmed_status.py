from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Hotel", "0003_alter_tablee_location"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_status",
            field=models.CharField(
                choices=[
                    ("preparing", "Preparing"),
                    ("pending", "Pending"),
                    ("available", "Available"),
                    ("confirmed", "Confirmed"),
                ],
                max_length=20,
            ),
        ),
    ]