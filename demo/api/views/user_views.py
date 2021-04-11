from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt import
from django.contrib.auth.models import User
from django.http import JsonResponse

from demo.api.models import UserSerializer

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return JsonResponse(serializer.data)