from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from ..models import License, LicenseRenewal
from ..serializers import LicenseSerializer, LicenseRenewalSerializer

class LicenseViewSet(viewsets.ModelViewSet):
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]
    queryset = License.objects.none()

    def get_queryset(self):
        return License.objects.filter(user=self.request.user)

class LicenseRenewalViewSet(viewsets.ModelViewSet):
    serializer_class = LicenseRenewalSerializer
    permission_classes = [IsAuthenticated]
    queryset = LicenseRenewal.objects.none()

    def get_queryset(self):
        if self.request.user.is_staff:
            return LicenseRenewal.objects.all()
        return LicenseRenewal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        if not request.user.is_staff:
            return Response({
                'error': 'No tienes permisos para realizar esta acción'
            }, status=status.HTTP_403_FORBIDDEN)

        renewal = self.get_object()
        action = request.data.get('action')

        try:
            if action == 'approve':
                license = License.objects.get(user=renewal.user)
                
                if license.expiration_date < timezone.now():
                    license.expiration_date = timezone.now()
                
                license.expiration_date = license.expiration_date + relativedelta(days=renewal.days_requested)
                license.active = True
                license.save()

                renewal.status = 'aprobada'
                renewal.processed_at = timezone.now()
                renewal.save()

                return Response({'message': 'Renovación aprobada correctamente'})

            elif action == 'reject':
                renewal.status = 'rechazada'
                renewal.processed_at = timezone.now()
                renewal.notes = request.data.get('rejection_reason', '')
                renewal.save()

                return Response({'message': 'Renovación rechazada'})

            return Response({
                'error': 'Acción no válida'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)