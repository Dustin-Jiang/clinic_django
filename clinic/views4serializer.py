from .serializers import ClinicUserSerializer
from rest_framework import views, viewsets
from rest_framework.response import Response
from .models import ClinicUser
from django.contrib.auth import get_user

class ClinicUserViewSet(viewsets.ModelViewSet):
    queryset = ClinicUser.objects.all()
    serializer_class = ClinicUserSerializer

class ClinicUserView(views.APIView):
    def get(self, request):
        context = {
            "request": request
        }
        serializer = ClinicUserSerializer(request.user, context=context)
        return Response(serializer.data)
