from django.urls import path
from . import views 
urlpatterns = [
    path('home/',views.home,name='home'),
    # path('login/',views.login,name='login'),
    path('index/',views.index,name='index'),
    # path('register/',views.register,name='register'),
    path('login_view/',views.login_view,name='login_view'),
    path('logout_view/',views.logout_view,name='logout_view'),
    path('register_view/',views.register_view,name='register_view'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('predict/', views.predict_future_hotspot, name='predict_future_hotspot'),
    # path('result/', views.prediction_result, name='prediction_result'),
    path('map/',views.map_view,name='map_view'),
    path("visualizations/", views.visualization_view, name="visualizations"),  
    path('profile/', views.profile_view, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
]
