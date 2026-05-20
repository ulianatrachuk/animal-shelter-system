from django.urls import path
from .views import AnalyticsAPIView, VolunteerAnalyticsAPIView, admin_analytics_view

urlpatterns = [
    path("", AnalyticsAPIView.as_view(), name="analytics"),
    path("me/", VolunteerAnalyticsAPIView.as_view(), name="volunteer-analytics-api"),
    path("dashboard/", admin_analytics_view, name="admin-analytics"),
]