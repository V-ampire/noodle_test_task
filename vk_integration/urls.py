from django.urls import path

from vk_integration import views


app_name = 'vk'

urlpatterns = [
    path('group/<int:group_id>/', views.GroupView.as_view(), name='group_info')
]