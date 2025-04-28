from django.db import models
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth.models import AbstractUser, Group, Permission
from .managers import UserManager


def upload_to(instance, filename): 
    return 'user/{filename}'.format(filename=filename)

 

class User(AbstractUser):
    username = None  # Remove username field
    first_name = None
    last_name = None
    email = models.EmailField(unique=True)  # Ensure email is unique and required
    name = models.CharField(max_length=150, default='')
    image = models.ImageField(_('Image'), upload_to=upload_to, blank=True, default='cat-user.jpeg')

    age = models.IntegerField(default=18)
    calories_d = models.IntegerField(null=True)
    protein_d = models.IntegerField(null=True)
    carbohydrate_d = models.IntegerField(null=True)
    fat_d = models.IntegerField(null=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(default=0)
    activity_level = models.IntegerField(default=1)
    gender = models.CharField(max_length=10, default='woman')
    goal = models.CharField(max_length=20, default='loss')
    favorite_dishes = models.ManyToManyField("Dish", related_name="favorited_by", blank=True)
    balance = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'  # Set email as the primary username field
    REQUIRED_FIELDS = ['name']  # List required fields other than email

    objects = UserManager()  

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


    def toggle_favorite(self, dish):
        """Toggle the favorite status of a dish for the user"""
        if dish in self.favorite_dishes.all():
            self.favorite_dishes.remove(dish)
            return False  # Dish removed from favorites
        else:
            self.favorite_dishes.add(dish)
            return True  # Dish added to favorites

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
    calories =models.IntegerField()
    protein = models.DecimalField(max_digits=10, decimal_places=1)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=1)
    fat = models.DecimalField(max_digits=10, decimal_places=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productAuthor', default=2)

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
    protein = models.DecimalField(max_digits=10, decimal_places=1)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=1)
    fat = models.DecimalField(max_digits=10, decimal_places=1)
    protein_100 = models.DecimalField(max_digits=10, decimal_places=1)
    carbohydrate_100 = models.DecimalField(max_digits=10, decimal_places=1)
    fat_100 = models.DecimalField(max_digits=10, decimal_places=1)
    drink = models.BooleanField(default=False)
    weight = models.IntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='dish', null=True, blank=True)
    portion = models.IntegerField(default=100, null=True, blank=True)
    portions = models.IntegerField(default=1, null=True, blank=True)
    description = models.TextField(default='', blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='dishAuthor', default=2, null=True)
    weight_of_ready_product = models.IntegerField(default=0, null=True, blank=True)
    is_popular = models.BooleanField(default=False)
 

    def save(self, *args, **kwargs):
        if not self.image:
            self.image = 'drink.jpeg' if self.drink else 'dish.jpeg'

        if self.weight_of_ready_product is None:  # Set default only if not provided
            self.weight_of_ready_product = self.weight
        
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='ingredientsProduct', null=True)
    calories = models.IntegerField()
    protein = models.DecimalField(max_digits=10, decimal_places=1)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=1)
    fat = models.DecimalField(max_digits=10, decimal_places=1)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='ingredientsDish')
    weight = models.IntegerField(default=0)
    name = models.CharField(default='')



class DiaryRecord(models.Model):
    name = models.CharField(max_length=150, default='food')
    dish = models.ForeignKey(Dish, on_delete=models.SET_NULL, related_name='diaryDish', null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    calories = models.IntegerField(null=True)
    protein = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    fat = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    weight = models.IntegerField(default=0)
    portions = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', default=2, null=True)


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Exercise(models.Model):
    name = models.CharField(max_length=100)
    met = models.FloatField()  # MET value
    is_weight_based = models.BooleanField(default=False)
    supports_reps = models.BooleanField(default=True)
    supports_time = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class WorkoutTemplate(models.Model):
    name = models.CharField(max_length=100)
    exercises = models.ManyToManyField(Exercise, through='WorkoutExercise')
    total_calories = models.PositiveIntegerField(default=0)


class WorkoutExercise(models.Model):
    workout = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    reps = models.PositiveIntegerField(null=True, blank=True)
    sets = models.PositiveIntegerField(null=True, blank=True, default=1)
    time_minutes = models.FloatField(null=True, blank=True)
    weight_group = models.CharField(max_length=20, choices=[
        ('none', 'None'),
        ('1-5', '1–5kg'),
        ('5-10', '5–10kg'),
        ('10-15', '10–15kg'),
        ('15+', '15kg+'),
    ], default='none')


class TabataTemplate(models.Model):
    name = models.CharField(max_length=100)
    exercises = models.ManyToManyField(Exercise)  # performed as tabata
    rounds = models.PositiveIntegerField(default=8)
    work_seconds = models.PositiveIntegerField(default=20)
    rest_seconds = models.PositiveIntegerField(default=10)
    duration = models.PositiveIntegerField(default=4)

 
class ActivityRecord(models.Model):
    ACTIVITY_TYPES = [
        ('custom_workout', 'Custom Workout'),
        ('workout_template', 'Workout Template'),
        ('tabata', 'Tabata'),
        ('run', 'Run'),
        ('walk_time', 'Walk (Time)'),
        ('walk_steps', 'Walk (Steps)'),
        ('interval_run', 'Interval Run'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, default='walk_time')
    related_id = models.PositiveIntegerField(null=True, blank=True)  # e.g. for template ID
    duration_minutes = models.FloatField(null=True, blank=True)
    steps = models.PositiveIntegerField(null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField()  # save user’s weight at time of activity
    calories_burned = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
