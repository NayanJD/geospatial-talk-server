from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt import
from django.http import JsonResponse

from demo.api.models import Factory, FactorySerializer

class FactoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = Factory.objects.all()
        serializer = FactorySerializer(user, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        serializer = FactorySerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return JsonResponse(serializer.data)