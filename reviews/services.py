import json
import re

from openai import OpenAI
from django.conf import settings

from .models import BehaviorComment, AnimalTraitSuggestion


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _extract_json_from_ai_response(content):
    content = content.strip()

    if content.startswith("```"):
        content = re.sub(r"^```json", "", content)
        content = re.sub(r"^```", "", content)
        content = re.sub(r"```$", "", content)
        content = content.strip()

    return json.loads(content)


def analyze_comments_for_animal(animal):
    print("AI STARTED for:", animal.name)

    comments = (
        BehaviorComment.objects
        .filter(animal=animal)
        .exclude(comment="")
        .order_by("-created_at")[:10]
    )

    texts = [comment.comment for comment in comments]

    print("COMMENTS:", texts)

    if len(texts) < 2:
        print("NOT ENOUGH DATA")
        return

    prompt = f"""
Проаналізуй коментарі волонтерів про собаку "{animal.name}".

Коментарі:
{texts}

Завдання:
1. Знайди повторювану поведінку або особливість.
2. Запропонуй коротку назву критерію українською мовою.
3. Напиши коротке пояснення для адміністратора.

Важливо:
- Якщо коментарі справді вказують на одну схожу проблему/особливість, створи пропозицію.
- Критерій має стосуватися тільки собаки "{animal.name}".
- Відповідь поверни тільки у JSON без markdown.

Формат:
{{
    "trait_name": "Коротка назва критерію",
    "summary": "N волонтерів зазначили, що ...",
    "count": N
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ти допомагаєш адміністратору притулку аналізувати "
                        "коментарі волонтерів про поведінку собак."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content
        print("RAW AI RESPONSE:", content)

        data = _extract_json_from_ai_response(content)
        print("PARSED AI DATA:", data)

        trait_name = str(data.get("trait_name", "")).strip()
        summary = str(data.get("summary", "")).strip()
        count = int(data.get("count", len(texts)))

        if not trait_name:
            print("AI DID NOT RETURN TRAIT NAME")
            return

        if count < 2:
            print("AI COUNT TOO SMALL:", count)
            return

        suggestion, created = AnimalTraitSuggestion.objects.get_or_create(
            animal=animal,
            suggested_trait_name=trait_name,
            defaults={
                "summary": summary,
                "comments_count": count,
            },
        )

        if not created:
            suggestion.summary = summary
            suggestion.comments_count = count
            suggestion.is_rejected = False
            suggestion.save()
            print("SUGGESTION UPDATED:", suggestion)

        else:
            print("SUGGESTION CREATED:", suggestion)

    except Exception as e:
        print("AI ERROR:", e)