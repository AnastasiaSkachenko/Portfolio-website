from django.urls import path 
from .views.diary import  DiaryView
from .views.users import RegisterView,  LogoutView, ModifyUserView, GetUserView, CustomTokenObtainPairView, CustomTokenRefreshView, SendVerificationCodeView, VerifyCodeView, ResetPasswordView, TestingHere
from .views.products import ProductView,  GetProductNames, CheckProductExistsView
from .views.dishes import  DishView, GetDishNames, IsNameUnique,  getDishById, ToggleFavorite
from .views.ingredients import  IngredientView, getIngredientsInDish


urlpatterns = [
    path('test/', TestingHere.as_view()),

    path('products/', ProductView.as_view(), name='productCreateGet'), 

    path('ingredient/', IngredientView.as_view(), name='ingredientCreateGet'), 
    path('ingredient/<int:id>/', IngredientView.as_view(), name='ingredientEditDelete'), 

    path('dishes/', DishView.as_view(), name='dishCreateGet'), 
    path('dishIngredients/', getIngredientsInDish, name='getDishIngredients'),
    path('get-dish-by-id/<int:id>', getDishById, name='getDishByID'),
    path("dish/<int:dish_id>/favorite/", ToggleFavorite.as_view(), name="toggle_favorite"),

    path('diary-record/', DiaryView.as_view(), name='recordCreateGet'), 

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
