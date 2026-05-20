from datetime import timedelta

from django.db.models import Count, Avg
from django.shortcuts import render
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from walks.models import Walk
from animals.models import Animal
from users.models import VolunteerProfile
from reviews.models import BehaviorReview


def _get_period_dates(period: str):
    now = timezone.localtime()
    today = now.date()

    if period == "month":
        start_date = today - timedelta(days=29)
    else:
        period = "week"
        start_date = today - timedelta(days=29)

    return period, start_date, today


def _build_time_stats(filtered_walks):
    hour_labels = [
        "10:00", "11:00", "12:00", "13:00",
        "14:00", "15:00", "16:00", "17:00"
    ]
    hour_values = [0] * len(hour_labels)

    for walk in filtered_walks.exclude(planned_start_time__isnull=True):
        hour = walk.planned_start_time.hour
        if 10 <= hour <= 17:
            hour_values[hour - 10] += 1

    peak_time = "-"
    if any(hour_values):
        peak_time = hour_labels[hour_values.index(max(hour_values))]

    return hour_labels, hour_values, peak_time


def _build_weekday_stats(filtered_walks):
    weekday_labels = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
    weekday_values = [0] * 7

    for walk in filtered_walks.exclude(planned_date__isnull=True):
        weekday_values[walk.planned_date.weekday()] += 1

    return weekday_labels, weekday_values


def build_analytics_data(period="week"):
    period, start_date, end_date = _get_period_dates(period)

    walks_qs = Walk.objects.filter(
        status="completed",
        ended_at__isnull=False
    )

    animals_qs = Animal.objects.all()
    volunteers_qs = VolunteerProfile.objects.all()
    reviews_qs = BehaviorReview.objects.all()

    filtered_walks = walks_qs.filter(
        planned_date__gte=start_date,
        planned_date__lte=end_date
    )

    total_walks = walks_qs.count()
    total_animals = animals_qs.count()
    total_volunteers = volunteers_qs.count()

    total_reviews = reviews_qs.filter(
        walk__status="completed",
        walk__ended_at__isnull=False
    ).values("walk").distinct().count()

    weekly_walks = filtered_walks.count()

    weekly_animals = 0
    if hasattr(Animal, "created_at"):
        weekly_animals = animals_qs.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).count()

    weekly_volunteers = 0
    if hasattr(VolunteerProfile, "created_at"):
        weekly_volunteers = volunteers_qs.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).count()

    weekly_reviews = reviews_qs.filter(
        walk__status="completed",
        walk__ended_at__isnull=False,
        walk__planned_date__gte=start_date,
        walk__planned_date__lte=end_date
    ).values("walk").distinct().count()

    hour_labels, hour_values, peak_time = _build_time_stats(filtered_walks)
    weekday_labels, weekday_values = _build_weekday_stats(filtered_walks)

    top_animals = (
        filtered_walks.values("animal__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    top_animals_labels = [item["animal__name"] or "—" for item in top_animals]
    top_animals_values = [item["total"] for item in top_animals]

    avg_scores = (
        reviews_qs.filter(
            walk__status="completed",
            walk__ended_at__isnull=False,
            walk__planned_date__gte=start_date,
            walk__planned_date__lte=end_date
        )
        .values("animal__name")
        .annotate(avg_score=Avg("score"))
        .order_by("-avg_score")[:5]
    )

    avg_scores_labels = [item["animal__name"] or "—" for item in avg_scores]
    avg_scores_values = [
        round(float(item["avg_score"]), 2)
        for item in avg_scores
        if item["avg_score"] is not None
    ]

    day_count = 7 if period == "week" else 30
    heatmap = []
    current = start_date

    walk_counts_by_day = {
        item["planned_date"]: item["total"]
        for item in filtered_walks.values("planned_date").annotate(total=Count("id"))
    }

    for _ in range(day_count):
        heatmap.append({
            "date": current.isoformat(),
            "label": current.strftime("%d.%m"),
            "weekday": current.weekday(),
            "count": walk_counts_by_day.get(current, 0),
        })
        current += timedelta(days=1)

    return {
        "summary": {
            "total_walks": total_walks,
            "total_animals": total_animals,
            "total_volunteers": total_volunteers,
            "total_reviews": total_reviews,
            "weekly_walks": weekly_walks,
            "weekly_animals": weekly_animals,
            "weekly_volunteers": weekly_volunteers,
            "weekly_reviews": weekly_reviews,
            "peak_time": peak_time,
            "top_animals": top_animals_labels[:2],
        },
        "period": period,
        "walks_by_time": {
            "labels": hour_labels,
            "values": hour_values,
        },
        "walks_by_weekday": {
            "labels": weekday_labels,
            "values": weekday_values,
        },
        "top_animals_labels": top_animals_labels,
        "top_animals_values": top_animals_values,
        "avg_scores_labels": avg_scores_labels,
        "avg_scores_values": avg_scores_values,
        "hour_labels": hour_labels,
        "hour_values": hour_values,
        "weekday_labels": weekday_labels,
        "weekday_values": weekday_values,
        "heatmap": heatmap,
        "total_walks": total_walks,
        "total_animals": total_animals,
        "total_volunteers": total_volunteers,
        "total_reviews": total_reviews,
        "weekly_walks": weekly_walks,
        "weekly_animals": weekly_animals,
        "weekly_volunteers": weekly_volunteers,
        "weekly_reviews": weekly_reviews,
        "title": "Аналітика притулку",
    }


def build_volunteer_analytics_data(volunteer_id, period="week"):
    period, start_date, end_date = _get_period_dates(period)

    walks_qs = Walk.objects.filter(
        volunteer_id=volunteer_id,
        status="completed",
        ended_at__isnull=False
    )

    filtered_walks = walks_qs.filter(
        planned_date__gte=start_date,
        planned_date__lte=end_date
    )

    total_walks = walks_qs.count()
    weekly_walks = filtered_walks.count()

    unique_animals_count = walks_qs.values("animal").distinct().count()
    weekly_unique_animals_count = filtered_walks.values("animal").distinct().count()

    hour_labels, hour_values, peak_time = _build_time_stats(filtered_walks)
    weekday_labels, weekday_values = _build_weekday_stats(filtered_walks)

    top_animals = (
        walks_qs.values("animal__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    top_animals_labels = [item["animal__name"] or "—" for item in top_animals]
    top_animals_values = [item["total"] for item in top_animals]

    return {
        "summary": {
            "total_walks": total_walks,
            "weekly_walks": weekly_walks,
            "unique_animals": unique_animals_count,
            "weekly_unique_animals": weekly_unique_animals_count,
            "peak_time": peak_time,
            "top_animals": top_animals_labels[:2],
        },
        "period": period,
        "walks_by_time": {
            "labels": hour_labels,
            "values": hour_values,
        },
        "walks_by_weekday": {
            "labels": weekday_labels,
            "values": weekday_values,
        },
        "top_animals_labels": top_animals_labels,
        "top_animals_values": top_animals_values,
        "title": "Моя аналітика",
    }


class AnalyticsAPIView(APIView):
    def get(self, request):
        period = request.GET.get("period", "week")
        data = build_analytics_data(period=period)
        return Response(data)


class VolunteerAnalyticsAPIView(APIView):
    def get(self, request):
        volunteer_id = request.GET.get("volunteer_id")

        if not volunteer_id:
            return Response(
                {"detail": "volunteer_id is required"},
                status=400
            )

        period = request.GET.get("period", "week")

        data = build_volunteer_analytics_data(
            volunteer_id=volunteer_id,
            period=period
        )

        return Response(data)


def admin_analytics_view(request):
    period = request.GET.get("period", "week")
    context = build_analytics_data(period=period)
    return render(request, "admin/analytics_dashboard.html", context)