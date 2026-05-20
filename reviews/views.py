from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import BehaviorTrait, BehaviorReview, BehaviorComment, AnimalSpecificTrait, AnimalSpecificTraitReview
from .serializers import (
    BehaviorTraitSerializer,
    BehaviorReviewSerializer,
    BehaviorCommentSerializer,
    AnimalSpecificTraitSerializer,
    AnimalSpecificTraitReviewSerializer
)

class BehaviorTraitListAPIView(APIView):
    def get(self, request):
        traits = BehaviorTrait.objects.filter(is_active=True).order_by("name")
        serializer = BehaviorTraitSerializer(traits, many=True)
        return Response(serializer.data)


class BehaviorReviewListAPIView(APIView):
    def get(self, request):
        walk_id = request.GET.get("walk")
        animal_id = request.GET.get("animal")

        reviews = BehaviorReview.objects.all().order_by("-created_at")

        if walk_id:
            reviews = reviews.filter(walk_id=walk_id)

        if animal_id:
            reviews = reviews.filter(animal_id=animal_id)

        serializer = BehaviorReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class BehaviorReviewCreateAPIView(APIView):
    def post(self, request):
        serializer = BehaviorReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BehaviorReviewDetailAPIView(APIView):
    def get(self, request, pk):
        review = get_object_or_404(BehaviorReview, pk=pk)
        serializer = BehaviorReviewSerializer(review)
        return Response(serializer.data)
    

class BehaviorCommentCreateAPIView(APIView):
    def post(self, request):
        serializer = BehaviorCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class AnimalSpecificTraitsByAnimalAPIView(APIView):
    def get(self, request, animal_id):
        traits = AnimalSpecificTrait.objects.filter(animal_id=animal_id)
        serializer = AnimalSpecificTraitSerializer(traits, many=True)
        return Response(serializer.data)


class AnimalSpecificTraitReviewCreateAPIView(APIView):
    def post(self, request):
        animal_id = request.data.get("animal")
        walk_id = request.data.get("walk")
        volunteer_id = request.data.get("volunteer")
        trait_id = request.data.get("trait")
        answer = request.data.get("answer")

        if animal_id is None or walk_id is None or volunteer_id is None or trait_id is None:
            return Response(
                {"detail": "animal, walk, volunteer and trait are required"},
                status=400
            )

        review, created = AnimalSpecificTraitReview.objects.update_or_create(
            walk_id=walk_id,
            volunteer_id=volunteer_id,
            trait_id=trait_id,
            defaults={
                "animal_id": animal_id,
                "answer": answer,
            }
        )

        serializer = AnimalSpecificTraitReviewSerializer(review)
        return Response(serializer.data, status=201 if created else 200)