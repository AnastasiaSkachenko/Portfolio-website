from django.db import models
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth.models import AbstractUser, Group, Permission
from .managers import UserManager
from caloriesCounter.utils import calculate_calories_from_activity_record
import uuid

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
    carbs_d = models.IntegerField(null=True)
    fat_d = models.IntegerField(null=True)
    fiber_d = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars_d = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    caffeine_d = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(default=0)
    activity_level = models.IntegerField(default=1)
    calculate_nutritions_from_activity_level = models.BooleanField(default=False)
    bmr = models.PositiveIntegerField(default=0)
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

class ProductOld(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True)  # Step 1
    name = models.CharField(max_length=180, unique=True)
    image = models.ImageField(_('Image'), upload_to=upload_products_to ,default='product.jpeg')
    calories =models.IntegerField()
    protein = models.DecimalField(max_digits=10, decimal_places=1)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=1)
    fat = models.DecimalField(max_digits=10, decimal_places=1)
    fiber = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    caffein = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productAuthor', default=2)
    last_updated = models.DateTimeField(auto_now=True)


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=None, editable=True)
    name = models.CharField(max_length=180, unique=True)
    image = models.ImageField(_('Image'), upload_to=upload_products_to ,default='product.jpeg')
    calories =models.IntegerField()
    protein = models.DecimalField(max_digits=10, decimal_places=1)
    carbs = models.DecimalField(max_digits=10, decimal_places=1)
    fat = models.DecimalField(max_digits=10, decimal_places=1)
    fiber = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    caffeine = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productUser', default=2)
    last_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4()
        super().save(*args, **kwargs)


class ProductMedia(models.Model):
    product = models.ForeignKey(Product, related_name="media", on_delete=models.CASCADE)
    file = models.FileField(upload_to="product_media/")

    # optional: identify type
    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)

    def save(self, *args, **kwargs):
        if not self.media_type:
            # infer type from file extension
            if self.file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                self.media_type = 'image'
            elif self.file.name.lower().endswith(('.mp4', '.mov', '.avi', '.webm')):
                self.media_type = 'video'
        super().save(*args, **kwargs)


class DishOld(models.Model):
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
    fat = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    fiber = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    caffein = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    protein_100 = models.DecimalField(max_digits=10, decimal_places=1)
    carbohydrate_100 = models.DecimalField(max_digits=10, decimal_places=1)
    fat_100 = models.DecimalField(max_digits=10, decimal_places=1)
    fiber_100 = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars_100 = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    caffein_100 = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    drink = models.BooleanField(default=False)
    weight = models.IntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_old = models.ForeignKey(ProductOld, on_delete=models.CASCADE, related_name='dish', null=True, blank=True)
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


class Dish(models.Model):
    TYPE_CHOICES = [
        ('pre_made', 'pre-made'),
        ('custom', 'custom'),
    ] 

    id = models.UUIDField(primary_key=True, default=None, editable=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='custom')
    name = models.CharField(max_length=180, unique=True)
    image = models.ImageField(_('Image'), upload_to=upload_dishes_to, blank=True)
    calories = models.IntegerField()
    protein = models.DecimalField(max_digits=10, decimal_places=1)
    carbs = models.DecimalField(max_digits=10, decimal_places=1)
    fat = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    fiber = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    caffeine = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    calories_100 = models.IntegerField(default=0)
    protein_100 = models.DecimalField(max_digits=10, decimal_places=1)
    carbs_100 = models.DecimalField(max_digits=10, decimal_places=1)
    fat_100 = models.DecimalField(max_digits=10, decimal_places=1)
    fiber_100 = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars_100 = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    caffeine_100 = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    drink = models.BooleanField(default=False)
    weight = models.IntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    product_old = models.ForeignKey(ProductOld, on_delete=models.CASCADE, related_name='old_product', null=True, blank=True)
    portion = models.IntegerField(default=100, null=True, blank=True)
    portions = models.IntegerField(default=1, null=True, blank=True)
    description = models.TextField(default='', blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='dishUser', default=2, null=True)
    weight_of_ready_product = models.IntegerField(default=0, null=True, blank=True)
    is_popular = models.BooleanField(default=False)
 
    is_deleted = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.image:
            self.image = 'drink.jpeg' if self.drink else 'dish.jpeg'

        if self.weight_of_ready_product is None:  # Set default only if not provided
            self.weight_of_ready_product = self.weight
        
        super().save(*args, **kwargs)

class DishMedia(models.Model):
    dish = models.ForeignKey(Dish, related_name="media", on_delete=models.CASCADE)
    file = models.FileField(upload_to="dish_media/")

    # optional: identify type
    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)

    def save(self, *args, **kwargs):
        if not self.media_type:
            # infer type from file extension
            if self.file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                self.media_type = 'image'
            elif self.file.name.lower().endswith(('.mp4', '.mov', '.avi', '.webm')):
                self.media_type = 'video'
        super().save(*args, **kwargs)


class IngredientOld(models.Model):
    product_old = models.ForeignKey(ProductOld, on_delete=models.SET_NULL, related_name='ingredientsProduct', null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    calories = models.IntegerField()
    protein = models.DecimalField(max_digits=10, decimal_places=1)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=1)
    fat = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    fiber = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    caffeine = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    dish_old = models.ForeignKey(DishOld, on_delete=models.CASCADE, related_name='ingredientsDishOld')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='ingredientsOldDish', null=True)
    weight = models.IntegerField(default=0)
    name = models.CharField(default='')



class Ingredient(models.Model):
    id = models.UUIDField(primary_key=True, default=None, editable=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    calories = models.IntegerField()
    protein = models.DecimalField(max_digits=10, decimal_places=1)
    carbs = models.DecimalField(max_digits=10, decimal_places=1)
    fat = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    fiber = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    caffeine = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='ingredientsDish', null=True)
    weight = models.IntegerField(default=0)
    name = models.CharField(default='')
    is_deleted = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)




class DiaryRecordOLD(models.Model):
    name = models.CharField(max_length=150, default='food')
    dish_old = models.ForeignKey(DishOld, on_delete=models.SET_NULL, related_name='diaryDish', null=True, blank=True)
    dish = models.ForeignKey(Dish, on_delete=models.SET_NULL, related_name='diaryDishUUID', null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    calories = models.IntegerField(null=True)
    protein = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    carbs = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    fat = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    fiber = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    caffeine = models.DecimalField(max_digits=10, decimal_places=1, default=0)

    weight = models.IntegerField(default=0)
    portions = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', default=2, null=True)

class DiaryRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=None, editable=True)
    name = models.CharField(max_length=150, default='food')
    dish = models.ForeignKey(Dish, on_delete=models.SET_NULL, related_name='diaryDishUUIDOwn', null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    calories = models.IntegerField(null=True)
    protein = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    carbs = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    fat = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    fiber = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    sugars = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    caffeine = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    weight = models.IntegerField(default=0)
    portions = models.IntegerField(default=0)
    is_deleted= models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userUUID', default=2, null=True)


 
class ActivityRecordOLD(models.Model):
    ACTIVITY_TYPES = [
        ('workout', 'Workout'),
        ('tabata', 'Tabata'),
        ('run', 'Run'),
        ('walk_time', 'Walk (Time)'),
        ('walk_steps', 'Walk (Steps)'),
        ('interval_run', 'Interval Run'),
        ('custom', 'Custom activity'),
        ('volleyball', "Volleyball"),
        ('stretching', 'Stretching'),
        ('jumping', 'Jumping'),
        ('home_chores', 'Home chores')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, default='walk_time')
    duration_minutes = models.FloatField(null=True, blank=True)
    steps = models.PositiveIntegerField(null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField() 
    intensity = models.PositiveIntegerField(default=3)
    calories_burned = models.FloatField()
    timestamp = models.DateTimeField(default=None, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.calories_burned:
            self.calories_burned = calculate_calories_from_activity_record(self)
        super().save(*args, **kwargs)


class DailyGoalsOLD(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=None, null=True, blank=True)
    calories_burned = models.PositiveIntegerField(default=0)    
    calories_burned_goal = models.PositiveIntegerField(default=0)
    protein = models.PositiveIntegerField(default=0)    
    protein_goal = models.PositiveIntegerField(default=0)
    carbohydrate = models.PositiveIntegerField(default=0)    
    carbohydrate_goal = models.PositiveIntegerField(default=0)
    fat = models.PositiveIntegerField(default=0)    
    fat_goal = models.PositiveIntegerField(default=0)
    fiber = models.PositiveIntegerField(default=0)
    fiber_goal = models.PositiveIntegerField(default=0)
    sugars = models.PositiveIntegerField(default=0)
    sugars_goal = models.PositiveIntegerField(default=0)
    caffeine = models.PositiveIntegerField(default=0)
    caffeine_goal = models.PositiveIntegerField(default=0)
    calories_intake = models.PositiveIntegerField(default=0)
    calories_intake_goal = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')




class ActivityRecord(models.Model):
    ACTIVITY_TYPES = [
        ('workout', 'Workout'),
        ('tabata', 'Tabata'),
        ('run', 'Run'),
        ('walk_time', 'Walk (Time)'),
        ('walk_steps', 'Walk (Steps)'),
        ('interval_run', 'Interval Run'),
        ('custom', 'Custom activity'),
        ('volleyball', "Volleyball"),
        ('stretching', 'Stretching'),
        ('jumping', 'Jumping'),
        ('home_chores', 'Home chores')
    ]

    id = models.UUIDField(primary_key=True, default=None, editable=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, default='walk_time')
    duration_minutes = models.FloatField(null=True, blank=True)
    steps = models.PositiveIntegerField(null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField() 
    intensity = models.PositiveIntegerField(default=3)
    calories_burned = models.FloatField()
    timestamp = models.DateTimeField(default=None, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    last_updated = models.DateTimeField(default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.calories_burned:
            self.calories_burned = calculate_calories_from_activity_record(self)
        super().save(*args, **kwargs)


class DailyGoals(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=None, null=True, blank=True)
    calories_burned = models.PositiveIntegerField(default=0)    
    calories_burned_goal = models.PositiveIntegerField(default=0)
    protein = models.PositiveIntegerField(default=0)    
    protein_goal = models.PositiveIntegerField(default=0)
    carbs = models.PositiveIntegerField(default=0)    
    carbs_goal = models.PositiveIntegerField(default=0)
    fat = models.PositiveIntegerField(default=0)    
    fat_goal = models.PositiveIntegerField(default=0)
    fiber = models.PositiveIntegerField(default=0)
    fiber_goal = models.PositiveIntegerField(default=0)
    sugars = models.PositiveIntegerField(default=0)
    sugars_goal = models.PositiveIntegerField(default=0)
    caffeine = models.PositiveIntegerField(default=0)
    caffeine_goal = models.PositiveIntegerField(default=0)
    calories_intake = models.PositiveIntegerField(default=0)
    calories_intake_goal = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')


