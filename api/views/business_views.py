from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Business
from ..serializers import BusinessSerializer
from ..licencePersmission import HasValidLicenseForReadOnly, HasValidLicenseForPublic

class BusinessViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasValidLicenseForReadOnly]
    serializer_class = BusinessSerializer
    queryset = Business.objects.none()

    def get_queryset(self):
        return Business.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        business = self.get_queryset().first()
        if business:
            serializer = self.get_serializer(business)
            return Response(serializer.data)
        return Response(None)

    def create(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            return Response(
                {"detail": "User already has a business"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PublicBusinessViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, HasValidLicenseForPublic]
    serializer_class = BusinessSerializer
    queryset = Business.objects.none()

    def get_queryset(self):
        return Business.objects.filter(is_public=True)

    # ... resto de los métodos 