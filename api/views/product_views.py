from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from ..models import Product
from ..serializers import ProductSerializer
from ..licencePersmission import HasValidLicenseForReadOnly
from ..mixins import BusinessFilterMixin

class ProductViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, HasValidLicenseForReadOnly]
    queryset = Product.objects.all()

