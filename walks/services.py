from datetime import datetime, timedelta
from django.utils import timezone

from walks.models import Walk
from notifications.models import Notification, AdminAlert


def check_missed_walks():
    now = timezone.localtime()

    walks = Walk.objects.filter(
        status="planned",
        started_at__isnull=True
    )

    for walk in walks:
        planned_datetime = timezone.make_aware(
            datetime.combine(walk.planned_date, walk.planned_start_time)
        )

        volunteer = walk.volunteer

        # 🔔 1. Нагадування на сьогодні
        if not walk.reminder_sent:
            if walk.planned_date == now.date():
                Notification.objects.create(
                    volunteer=volunteer,
                    title="Запланована прогулянка",
                    message=(
                        f"Сьогодні у вас прогулянка з {walk.animal.name} "
                        f"о {walk.planned_start_time.strftime('%H:%M')}"
                    )
                )
                Walk.objects.filter(id=walk.id).update(reminder_sent=True)

        # 🔔 2. Нагадування за 30 хв
        half_hour_before = planned_datetime - timedelta(minutes=30)

        if not walk.half_hour_reminder_sent:
            if half_hour_before <= now < planned_datetime:
                Notification.objects.create(
                    volunteer=volunteer,
                    title="Нагадування",
                    message=(
                        f"Ваша прогулянка з {walk.animal.name} "
                        "розпочнеться через 30 хвилин"
                    )
                )
                Walk.objects.filter(id=walk.id).update(
                    half_hour_reminder_sent=True
                )

        # ❌ 3. Пропуск після 30 хв
        deadline = planned_datetime + timedelta(minutes=30)

        if now >= deadline:
            Walk.objects.filter(id=walk.id).update(status="missed")

            volunteer.missed_walks_count += 1

            if volunteer.missed_walks_count == 1:
                message = (
                    "Ви пропустили прогулянку. Якщо це буде повторюватись надалі, "
                    "ми будемо вимушені заблокувати Ваш профіль."
                )
            elif volunteer.missed_walks_count == 2:
                message = (
                    "Ви знову пропустили прогулянку. Наступного разу Ваш профіль "
                    "буде заблоковано без можливості створити новий."
                )
            else:
                volunteer.is_blocked = True
                volunteer.blocked_at = timezone.now()
                volunteer.block_reason = (
                    "Користувач пропустив 3 заплановані прогулянки."
                )

                message = "Ваш профіль буде заблоковано впродовж цього дня."

                AdminAlert.objects.create(
                    volunteer=volunteer,
                    title="Потрібно перевірити блокування профілю",
                    message=(
                        f"Волонтер {volunteer.get_full_name()} пропустив "
                        f"{volunteer.missed_walks_count} прогулянки."
                    )
                )

            volunteer.save()

            Notification.objects.create(
                volunteer=volunteer,
                title="Попередження",
                message=message
            )