from django.contrib import admin
from django.urls import path, include
from .views import home  # Import the new view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/projects/', include('projects.urls')),
    path('', home),  # Add this line to handle requests to `/`
]
