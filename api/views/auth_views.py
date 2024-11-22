from rest_framework import viewsets, status
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from ..models import User, EmailVerificationToken, License
from ..serializers import UserSerializer
from ..permissions import IsOwnerOrNoAccess
import logging

logger = logging.getLogger(__name__)

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        identifier = request.data.get('username')
        password = request.data.get('password')
        
        try:
            # Buscar usuario por email si el identificador es un email
            if '@' in identifier:
                try:
                    user = User.objects.get(email__iexact=identifier)
                    identifier = user.username
                except User.DoesNotExist:
                    return Response({
                        'error': f'No existe una cuenta con el email {identifier}'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            
            user = authenticate(username=identifier, password=password)
            
            if not user:
                return Response({
                    'error': 'Credenciales inválidas'
                }, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_active:
                return Response({
                    'error': 'Esta cuenta no está activada'
                }, status=status.HTTP_401_UNAUTHORIZED)

            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username,
                'email': user.email
            })
                
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            return Response({
                'error': 'Error en el proceso de login'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def register(self, request):
        try:
            data = request.data.copy()
            serializer = UserSerializer(data=data)
            
            if serializer.is_valid():
                # Hashear la contraseña después de la validación pero antes de guardar
                validated_data = serializer.validated_data
                validated_data['password'] = make_password(validated_data['password'])
                user = serializer.save()
                
                user.is_active = True
                user.save()
                
                # Crear licencia gratuita
                License.objects.create(
                    user=user,
                    is_pro=False,
                    active=True
                )
                
                # Crear token para el usuario
                token, _ = Token.objects.get_or_create(user=user)
                
                return Response({
                    'token': token.key,
                    'user_id': user.pk,
                    'username': user.username,
                    'email': user.email,
                    'message': 'Usuario creado exitosamente'
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            request.user.auth_token.delete()
            return Response({
                'message': 'Sesión cerrada exitosamente'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Error al cerrar sesión'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)