from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from ..models import User
from ..serializers import UserSerializer

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.none()

    def list(self, request):
        return Response({
            "endpoints": {
                "login": "auth/login/",
                "logout": "auth/logout/", 
                "register": "auth/register/",
                "verify_email": "auth/verify-email/"
            }
        })

    @action(detail=False, methods=['post'])
    def login(self, request):
        identifier = request.data.get('username')  # puede ser username o email
        password = request.data.get('password')
        
        if not identifier or not password:
            return Response({
                'error': 'Por favor proporcione usuario/email y contraseña'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Determinar si el identificador es un email
        if '@' in identifier:
            try:
                user = User.objects.get(email=identifier)
                username = user.username
            except User.DoesNotExist:
                return Response({
                    'error': 'No existe una cuenta con este correo electrónico'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            username = identifier

        # Intentar autenticar
        user = authenticate(username=username, password=password)
        
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
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            request.user.auth_token.delete()
            return Response({
                'mensaje': 'Sesión cerrada exitosamente'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Error al cerrar sesión'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            
            try:
                # Enviar email de verificación
                send_mail(
                    'Verificación de cuenta',
                    'Bienvenido a Mi Empresa Virtual. Por favor verifica tu cuenta.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error enviando email: {str(e)}")

            return Response({
                'token': token.key,
                'usuario': serializer.data,
                'mensaje': 'Usuario registrado exitosamente'
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        })