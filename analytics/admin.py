from django.contrib import admin
from django.urls import path
from .views import admin_analytics_view


class AnalyticsAdminSiteExtension:
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "analytics-dashboard/",
                self.admin_view(admin_analytics_view),
                name="analytics-dashboard",
            ),
        ]
        return custom_urls + urls


admin.site.__class__ = type(
    "CustomAdminSite",
    (AnalyticsAdminSiteExtension, admin.site.__class__),
    {},
)