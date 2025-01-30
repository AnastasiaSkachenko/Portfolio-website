from django.urls import path 
from .views import send_confirmation, get_skill, get_project
from .viewsCaloriesCounter import ProductView, IngredientView, DishView, getIngredientsInDish, DiaryView, getDishById
from .user_views import RegisterView, LoginView, LogoutView, ModifyUserView

urlpatterns = [
    path('send-confirmation/', send_confirmation, name='send_confirmation'), 
    path('get-project/', get_project, name='get_project'), 
    path('get-skill/', get_skill, name='get_skill'),

    path('products/', ProductView.as_view(), name='productCreateGet'), 

    path('ingredient/', IngredientView.as_view(), name='ingredientCreateGet'), 
    path('ingredient/<int:id>/', IngredientView.as_view(), name='ingredientEditDelete'), 

    path('dishes/', DishView.as_view(), name='dishCreateGet'), 
    path('dishIngredients/', getIngredientsInDish, name='getDishIngredients'),
    path('get-dish-by-id/<int:id>', getDishById, name='getDishByID'),

    path('diary-record/', DiaryView.as_view(), name='recordCreateGet'), 
    path('diary-record/<int:id>/', DiaryView.as_view(), name='recordEditDelete'), 

    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("modify-user/", ModifyUserView.as_view(), name="modify-user"),

]
