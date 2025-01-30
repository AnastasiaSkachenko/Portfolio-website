from django.db import models
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth.models import AbstractUser, Group, Permission


def upload_to(instance, filename): 
    return 'user/{filename}'.format(filename=filename)

 

class User(AbstractUser):
    username = None  # Remove username field
    first_name = None
    last_name = None
    email = models.EmailField(unique=True)  # Ensure email is unique and required

    name = models.CharField(max_length=150, default='')
    age = models.IntegerField(default=18)
    image = models.ImageField(_('Image'), upload_to=upload_to, blank=True)
    calories_d = models.IntegerField(null=True)
    protein_d = models.IntegerField(null=True)
    carbohydrate_d = models.IntegerField(null=True)
    fat_d = models.IntegerField(null=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(default=0)
    activity_level = models.IntegerField(default=1)
    USERNAME_FIELD = 'email'  # Set email as the primary username field
    REQUIRED_FIELDS = ['name']  # List required fields other than email


    groups = models.ManyToManyField(
        Group,
        related_name='backend_user_set',  # Custom related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='backend_user_permissions_set',  # Custom related_name
        blank=True
    )

    def __str__(self):
        return self.email


 

def upload_products_to(instance, filename): 
    return 'products/{filename}'.format(filename=filename)

def upload_dishes_to(instance, filename): 
    return 'dishes/{filename}'.format(filename=filename)


class Project(models.Model):
    name = models.CharField(max_length=180)
    description = models.TextField()
    tools = models.TextField()

class Skill(models.Model):
    name = models.CharField(max_length=180)
    image = models.CharField(max_length=180)
    experience = models.IntegerField()

class Product(models.Model):
    name = models.CharField(max_length=180)
    image = models.ImageField(_('Image'), upload_to=upload_products_to ,default='product.jpeg')
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbohydrate = models.IntegerField()
    fat = models.IntegerField()

class Dish(models.Model):
    TYPE_CHOICES = [
        ('pre_made', 'pre-made'),
        ('custom', 'custom'),
    ] 
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='custom')
    name = models.CharField(max_length=180)
    image = models.ImageField(_('Image'), upload_to=upload_dishes_to, blank=True)
    calories = models.IntegerField()
    calories_100 = models.IntegerField(default=0)
    protein = models.IntegerField()
    carbohydrate = models.IntegerField()
    fat = models.IntegerField()
    protein_100 = models.IntegerField(default=0)
    carbohydrate_100 = models.IntegerField(default=0)
    fat_100 = models.IntegerField(default=0)
    drink = models.BooleanField(default=False)
    weight = models.IntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='dish', null=True, blank=True)
    portion = models.IntegerField(default=100, null=True, blank=True)
    portions = models.IntegerField(default=1, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.image:
            self.image = 'drink.jpeg' if self.drink else 'dish.jpeg'
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ingredientsProduct')
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbohydrate = models.IntegerField()
    fat = models.IntegerField()
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='ingredientsDish')
    weight = models.IntegerField(default=0)


class DiaryRecord(models.Model):
    name = models.CharField(max_length=150, default='')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='diaryDish', null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    calories = models.IntegerField(null=True)
    protein = models.IntegerField(null=True)
    carbohydrate = models.IntegerField(null=True)
    fat = models.IntegerField(null=True)
    weight = models.IntegerField(default=0)
    portions = models.IntegerField(default=0)

