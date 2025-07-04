from django.urls import path 
from .views.diary import  DiaryView, DailyGoalView, GetAllDiaryRecords, GetUpdatedDiaryRecords
from .views.users import RegisterView,  LogoutView, ModifyUserView, GetUserView, CustomTokenObtainPairView, CustomTokenRefreshView, SendVerificationCodeView, VerifyCodeView, ResetPasswordView, TestingHere
from .views.products import ProductView,  GetProductNames, CheckProductExistsView, GetUpdatedProducts, GetAllProducts, ping
from .views.dishes import  DishView, GetDishNames, IsNameUnique,  getDishById, ToggleFavorite, GetAllDishes, GetUpdatedDishes
from .views.ingredients import  IngredientView, getIngredientsInDish, GetAllIngredients, GetUpdatedIngredients
from .views.activity import ActivityRecordView, GetAllActivities, GetUpdatedActivities
from .views.statistics import get_monthly_nutrition_stats




urlpatterns = [
    path("ping/", ping),

    path('dailyGoals/', DailyGoalView.as_view()),

    path('activityRecords/', ActivityRecordView.as_view()),
    path('activityRecords-all/', GetAllActivities.as_view(), name='getAllActivityRecords'), 
    path('activityRecords-updated/', GetUpdatedActivities.as_view(), name='getUpdatedActivityRecords'), 

    path('statistics/', get_monthly_nutrition_stats, name='getMonthlyNutritionStats'),


    path('test/', TestingHere.as_view()),

    path('products/', ProductView.as_view(), name='productCreateGet'), 
    path('products-all/', GetAllProducts.as_view(), name='getAllProducts'), 
    path('products-updated/', GetUpdatedProducts.as_view(), name='getUpdatedProducts'), 

    path('ingredient/', IngredientView.as_view(), name='ingredientCreateGet'), 
    path('ingredient/<str:id>', IngredientView.as_view(), name='ingredientEditDelete'), 

    path('ingredients-all/', GetAllIngredients.as_view(), name='getAllIngredients'), 
    path('ingredients-updated/', GetUpdatedIngredients.as_view(), name='getUpdatedIngredients'), 


    path('dishes/', DishView.as_view(), name='dishCreateGet'), 

    path('dishes-all/', GetAllDishes.as_view(), name='getAllDishes'), 
    path('dishes-updated/', GetUpdatedDishes.as_view(), name='getUpdatedDishes'), 

    path('dishIngredients/', getIngredientsInDish, name='getDishIngredients'),
    path('get-dish-by-id/<int:id>', getDishById, name='getDishByID'),
    path("dish/<int:dish_id>/favorite/", ToggleFavorite.as_view(), name="toggle_favorite"),

    path('diary-record/', DiaryView.as_view(), name='recordCreateGet'), 
    path('diary-record-all/', GetAllDiaryRecords.as_view(), name='getAllDailyRecords'), 
    path('diary-record-updated/', GetUpdatedDiaryRecords.as_view(), name='getUpdatedDiaryRecords'), 


    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("modify-user/", ModifyUserView.as_view(), name="modify-user"),
    path("user/", GetUserView.as_view(), name='getUser'),

    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),  # Refresh


    path('products/names/', GetProductNames.as_view(), name='productNames'),
    path('checkProductName/', CheckProductExistsView.as_view(), name='checkNameExist'),

    path('dishes/names/',  GetDishNames.as_view(), name='getDishNames'),
    path('isNameUnique/', IsNameUnique.as_view(), name='isNameUnique'),
    

    path("send-code/", SendVerificationCodeView.as_view(), name="send-code"),
    path("verify-code/", VerifyCodeView.as_view(), name="verify-code"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),

 

]


