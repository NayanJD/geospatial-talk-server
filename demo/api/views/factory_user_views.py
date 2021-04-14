from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from demo.api.models import (
    Factory,
    FactorySerializer,
    FactoryUser,
    FactoryUserSerializer,
)
from django.http import JsonResponse


class FactoryUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        factory_id = kwargs["pk"]

        users = FactoryUser.objects.filter(factory_id=factory_id)
        serializer = FactoryUserSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, **kwargs):
        factory_id = kwargs["pk"]

        factory = Factory.objects.get(pk=factory_id)

        serializer = FactoryUserSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save(factory=factory)

        return JsonResponse(serializer.data)
