from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import *
from .serializers import *
from .permissions import IsOwnerOrNoAccess,OnlyOwnerAccess
from django.shortcuts import render
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .licencePersmission import HasValidLicense
import logging
from .mixins import BusinessFilterMixin
from rest_framework.decorators import action
from django.db import transaction
from decimal import Decimal
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger(__name__)

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [  HasValidLicense,OnlyOwnerAccess]

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

    @action(detail=False, methods=['post'])
    def register_sale(self, request):
        try:
            with transaction.atomic():
                # Obtener datos
                product_id = request.data.get('product')
                quantity = int(request.data.get('quantity'))
                unit_price = Decimal(request.data.get('unit_price'))
                is_credit = request.data.get('is_credit', False)
                card_id = request.data.get('card')
                
                # Validar producto y stock
                product = Product.objects.get(id=product_id)
                if product.stock < quantity:
                    return Response(
                        {'error': 'No hay suficiente stock disponible'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Crear la venta
                sale_data = request.data.copy()
                sale_data['business'] = product.business.id
                serializer = self.get_serializer(data=sale_data)
                serializer.is_valid(raise_exception=True)
                sale = serializer.save()

                # Actualizar stock del producto
                product.stock -= quantity
                product.save()

                # Si no es a crédito y hay tarjeta, actualizar saldo
                if not is_credit and card_id:
                    card = Card.objects.get(id=card_id)
                    total_amount = quantity * unit_price
                    card.balance += total_amount
                    card.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Card.DoesNotExist:
            return Response(
                {'error': 'Tarjeta no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def undo_sale(self, request, pk=None):
        try:
            with transaction.atomic():
                sale = self.get_object()
                quantity = sale.quantity
                unit_price = sale.unit_price
                product_id = sale.product_id
                card_id = sale.card_id if hasattr(sale, 'card') else None
                is_credit = sale.is_credit

                # Actualizar stock del producto si existe
                try:
                    product = Product.objects.get(id=product_id)
                    product.stock += quantity
                    product.save()
                except Product.DoesNotExist:
                    pass

                # Actualizar saldo de la tarjeta si aplica
                if not is_credit and card_id:
                    try:
                        card = Card.objects.get(id=card_id)
                        total_amount = quantity * unit_price
                        card.balance -= total_amount
                        card.save()
                    except Card.DoesNotExist:
                        pass

                # Eliminar la venta
                sale.delete()

                return Response({'message': 'Venta deshecha exitosamente'}, 
                              status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PurchaseViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def register_purchase(self, request):
        try:
            with transaction.atomic():
                # Obtener datos
                product_id = request.data.get('product')
                quantity = int(request.data.get('quantity'))
                unit_price = Decimal(request.data.get('unit_price'))
                is_credit = request.data.get('is_credit', False)
                card_id = request.data.get('card')
                
                # Validar producto
                product = Product.objects.get(id=product_id)
                
                # Calcular monto total
                total_amount = quantity * unit_price

                # Si no es a crédito y hay tarjeta, verificar saldo
                if not is_credit and card_id:
                    card = Card.objects.get(id=card_id)
                    if card.balance < total_amount:
                        return Response(
                            {'error': 'Saldo insuficiente en la tarjeta'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Crear la compra
                purchase_data = request.data.copy()
                purchase_data['business'] = product.business.id
                serializer = self.get_serializer(data=purchase_data)
                serializer.is_valid(raise_exception=True)
                purchase = serializer.save()

                # Actualizar stock del producto
                product.stock += quantity
                product.save()

                # Si no es a crédito y hay tarjeta, actualizar saldo
                if not is_credit and card_id:
                    card.balance -= total_amount
                    card.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def undo_purchase(self, request, pk=None):
        try:
            with transaction.atomic():
                purchase = self.get_object()
                quantity = purchase.quantity
                unit_price = purchase.unit_price
                product_id = purchase.product_id
                
                # Obtener la tarjeta del request si se proporciona, sino usar la de la compra
                new_card_id = request.data.get('card_id')
                original_card_id = purchase.card_id if hasattr(purchase, 'card') else None
                card_id = new_card_id or original_card_id
                
                is_credit = purchase.is_credit

                # Validar que haya una tarjeta si la compra no fue a crédito
                if not is_credit and not card_id:
                    return Response(
                        {'error': 'Se requiere una tarjeta para deshacer una compra que no fue a crédito'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Actualizar stock del producto si existe
                try:
                    product = Product.objects.get(id=product_id)
                    if product.stock < quantity:
                        return Response(
                            {'error': 'No hay suficiente stock para deshacer la compra'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    product.stock -= quantity
                    product.save()
                except Product.DoesNotExist:
                    return Response(
                        {'error': 'El producto ya no existe'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Actualizar saldo de la tarjeta si aplica
                if not is_credit and card_id:
                    try:
                        card = Card.objects.get(id=card_id)
                        total_amount = quantity * unit_price
                        card.balance += total_amount
                        card.save()
                    except Card.DoesNotExist:
                        return Response(
                            {'error': 'La tarjeta seleccionada no existe'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Eliminar la compra
                purchase.delete()

                return Response(
                    {'message': 'Compra deshecha exitosamente'}, 
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ExpenseViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def register_expense(self, request):
        try:
            with transaction.atomic():
                # Obtener datos
                amount = Decimal(request.data.get('amount'))
                card_id = request.data.get('card')

                # Validar tarjeta y saldo
                if card_id:
                    card = Card.objects.get(id=card_id)
                    if card.balance < amount:
                        return Response(
                            {'error': 'Saldo insuficiente en la tarjeta'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Crear el gasto
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                expense = serializer.save()

                # Actualizar saldo de la tarjeta
                if card_id:
                    card.balance -= amount
                    card.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Card.DoesNotExist:
            return Response(
                {'error': 'Tarjeta no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def undo_expense(self, request, pk=None):
        try:
            with transaction.atomic():
                expense = self.get_object()
                amount = expense.amount
                card_id = expense.card_id if hasattr(expense, 'card') else None

                # Actualizar saldo de la tarjeta si existe
                if card_id:
                    try:
                        card = Card.objects.get(id=card_id)
                        card.balance += amount
                        card.save()
                    except Card.DoesNotExist:
                        pass

                # Eliminar el gasto
                expense.delete()

                return Response({'message': 'Gasto deshecho exitosamente'}, 
                              status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        identifier = request.data.get('username')  # Puede ser email o username
        password = request.data.get('password')
        
        try:
            # Si el identificador contiene @, buscar el usuario por email
            if '@' in identifier:
                try:
                    user = User.objects.get(email__iexact=identifier)
                    identifier = user.username  # Usar el username para autenticación
                except User.DoesNotExist:
                    return Response(
                        {'error': f'No existe una cuenta con el email {identifier}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Intentar autenticar con el username (original o encontrado por email)
            user = authenticate(username=identifier, password=password)
            
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user_id': user.pk,
                    'username': user.username
                })
            else:
                return Response(
                    {'error': 'Contraseña incorrecta'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': 'Error en el proceso de login'},
                status=status.HTTP_400_BAD_REQUEST
            )

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            
            if serializer.is_valid():
                # Crear usuario inactivo
                user = serializer.save()  # Ya está configurado para crear inactivo
                
                # Crear token de verificación
                verification_token = EmailVerificationToken.objects.create(user=user)
                
                # URL del frontend
                frontend_url = "https://e-comcuba.com"
                verification_url = f"{frontend_url}/verify-email/{verification_token.token}"
                
                # Enviar email
                send_mail(
                    'Verifica tu cuenta en Mi Empresa Virtual',
                    f'''
                    Hola {user.username},

                    Gracias por registrarte. Para activar tu cuenta, haz clic en el siguiente enlace:
                    {verification_url}

                    Este enlace expirará en 24 horas.

                    Saludos,
                    Mi Empresa Virtual
                    ''',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                
                # Crear licencia
                License.objects.create(
                    user=user,
                    is_pro=False,
                    active=True
                )
                
                return Response({
                    "message": "Usuario creado. Por favor verifica tu correo electrónico"
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Solo retorna productos públicos de negocios públicos
        return Product.objects.filter(is_public=True, business__is_public=True)

class PublicBusinessViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Solo retorna negocios públicos
        return Business.objects.filter(is_public=True)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrNoAccess, IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    permission_classes = []  # Permitir acceso público

    def get(self, request, token):
        try:
            # Verificar si el token existe
            try:
                verification_token = EmailVerificationToken.objects.get(token=token)
            except EmailVerificationToken.DoesNotExist:
                return Response({
                    'error': 'Link de verificación inválido o ya utilizado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si el usuario existe
            if not verification_token.user:
                verification_token.delete()
                return Response({
                    'error': 'Usuario no encontrado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si el token no ha expirado (24 horas)
            if (timezone.now() - verification_token.created_at).days >= 1:
                verification_token.delete()
                return Response({
                    'error': 'El link de verificación ha expirado. Por favor, solicita uno nuevo'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si el usuario ya está activo
            user = verification_token.user
            if user.is_active:
                verification_token.delete()
                return Response({
                    'error': 'Esta cuenta ya está verificada'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Activar usuario
            user.is_active = True
            user.save()
            
            # Eliminar token usado
            verification_token.delete()
            
            return Response({
                'message': '¡Email verificado exitosamente! Ya puedes iniciar sesión'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en verificación de email: {str(e)}")
            return Response({
                'error': 'Error al verificar el email. Por favor, intenta nuevamente'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)