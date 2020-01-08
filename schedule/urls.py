"""schedule URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from . import views

urlpatterns = [
    path('parse/<str:session_id>/', views.parse_session, name='Parse a session'),
    path('student_info/<str:session_id>/<str:api_key>', views.return_student_info, name='Student info'),
    path('week_schedule/<str:session_id>/<str:api_key>/<int:week>', views.return_schedule_week, name='Schedule for a week'),
    path('week_schedule_formated/<str:session_id>/<str:api_key>/<int:week>', views.return_schedule_week_formated, name='Schedule for a week'),
    path('week_periods/<str:session_id>/<str:api_key>/', views.return_week_period, name='Period for a week'),
    path('marks/<str:session_id>/<str:api_key>/<int:trimester>', views.return_week_period, name='Marks of the given trimester'),
]