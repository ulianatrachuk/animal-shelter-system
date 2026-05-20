from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Animal
from .serializers import AnimalSerializer


class AnimalListAPIView(APIView):
    def get(self, request):
        animals = Animal.objects.all().order_by("name")
        serializer = AnimalSerializer(animals, many=True, context={"request": request})
        return Response(serializer.data)


class AnimalDetailAPIView(APIView):
    def get(self, request, pk):
        animal = Animal.objects.get(pk=pk)
        serializer = AnimalSerializer(animal, context={"request": request})
        return Response(serializer.data)