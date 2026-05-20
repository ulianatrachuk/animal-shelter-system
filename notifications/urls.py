from django.urls import path

from .views import (
    NotificationListAPIView,
    MarkNotificationReadAPIView,
    AdminAlertListAPIView,
    ResolveAdminAlertAPIView,
)

urlpatterns = [
    path(
        "notifications/<int:profile_id>/",
        NotificationListAPIView.as_view(),
        name="notification-list"
    ),
    path(
        "notifications/<int:pk>/read/",
        MarkNotificationReadAPIView.as_view(),
        name="notification-read"
    ),
    path(
        "admin-alerts/",
        AdminAlertListAPIView.as_view(),
        name="admin-alert-list"
    ),
    path(
        "admin-alerts/<int:pk>/resolve/",
        ResolveAdminAlertAPIView.as_view(),
        name="admin-alert-resolve"
    ),
]