from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import *
from .serializers import *
from .permissions import IsOwnerOrNoAccess
from django.shortcuts import render
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .licencePersmission import HasValidLicense
import logging
from .mixins import BusinessFilterMixin

logger = logging.getLogger(__name__)

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [ IsOwnerOrNoAccess, HasValidLicense]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Business.objects.filter(user=self.request.user)

class ProductViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class SaleViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

class PurchaseViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

class ExpenseViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

class CardViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

class ContactViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

class LicenseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrNoAccess]

    def get_queryset(self):
        return License.objects.filter(user=self.request.user)

def api_welcome(request):
    return render(request, 'welcome.html')

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class RegisterView(APIView):
    def post(self, request):
        logger.info(f"Received data: {request.data}")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Crear licencia para el nuevo usuario
            License.objects.create(
                user=user,
                is_pro=False,
                active=True
            )
            return Response({"message": "Usuario creado exitosamente"}, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Solo retorna productos públicos
        return Product.objects.filter(is_public=True)

class PublicBusinessViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Retorna todos los negocios sin restricciones
        return Business.objects.all()