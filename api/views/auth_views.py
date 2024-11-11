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
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from django.http import HttpResponse

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
            
            try:
                # Generar token y uid para el link de verificación
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Crear el link de verificación que apunta al backend
                verification_url = f"https://api.finansas.e-comcuba.com/api/auth/verify-email/{uid}/{token}/"
                #verification_url = f"http://127.0.0.1:8000/api/auth/verify-email/{uid}/{token}/"
                # Enviar email de verificación
                subject = 'Verificación de cuenta'
                message = f'''
                Hola {user.username},
                
                Para verificar tu cuenta, haz clic en el siguiente enlace:
                {verification_url}
                
                Si no creaste esta cuenta, puedes ignorar este mensaje.
                '''
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

                return Response({
                    'usuario': serializer.data,
                    'mensaje': 'Usuario registrado exitosamente. Por favor verifica tu correo electrónico.'
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                user.delete()
                return Response({
                    'error': 'Error al enviar el correo de verificación'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='verify-email/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)')
    def verify_email(self, request, uidb64=None, token=None):
        try:
            # Decodificar el uid sin filtrar por is_active
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            # Verificar el token
            if default_token_generator.check_token(user, token):
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    return HttpResponse("""
                        <!DOCTYPE html>
                        <html lang="es">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Verificación de Cuenta</title>
                            <style>
                                body {
                                    font-family: Arial, sans-serif;
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    height: 100vh;
                                    margin: 0;
                                    background-color: #f5f5f5;
                                }
                                .container {
                                    text-align: center;
                                    padding: 2rem;
                                    background-color: white;
                                    border-radius: 8px;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                    max-width: 400px;
                                    width: 90%;
                                }
                                .success {
                                    color: #28a745;
                                }
                                .message {
                                    margin: 1rem 0;
                                    font-size: 1.1rem;
                                }
                                .login-link {
                                    display: inline-block;
                                    margin-top: 1rem;
                                    padding: 0.5rem 1rem;
                                    background-color: #007bff;
                                    color: white;
                                    text-decoration: none;
                                    border-radius: 4px;
                                    transition: background-color 0.3s;
                                }
                                .login-link:hover {
                                    background-color: #0056b3;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1 class="success">✓ Verificación Exitosa</h1>
                                <p class="message">¡Tu cuenta ha sido activada satisfactoriamente! Ya puedes iniciar sesión.</p>
                                <a href="http://localhost:3000/login" class="login-link">Ir a Iniciar Sesión</a>
                            </div>
                        </body>
                        </html>
                    """)
                else:
                    return HttpResponse("""
                        <!DOCTYPE html>
                        <html lang="es">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Cuenta ya verificada</title>
                            <style>
                                body {
                                    font-family: Arial, sans-serif;
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    height: 100vh;
                                    margin: 0;
                                    background-color: #f5f5f5;
                                }
                                .container {
                                    text-align: center;
                                    padding: 2rem;
                                    background-color: white;
                                    border-radius: 8px;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                    max-width: 400px;
                                    width: 90%;
                                }
                                .info {
                                    color: #17a2b8;
                                }
                                .message {
                                    margin: 1rem 0;
                                    font-size: 1.1rem;
                                }
                                .login-link {
                                    display: inline-block;
                                    margin-top: 1rem;
                                    padding: 0.5rem 1rem;
                                    background-color: #007bff;
                                    color: white;
                                    text-decoration: none;
                                    border-radius: 4px;
                                    transition: background-color 0.3s;
                                }
                                .login-link:hover {
                                    background-color: #0056b3;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1 class="info">ℹ Cuenta ya verificada</h1>
                                <p class="message">Esta cuenta ya ha sido verificada anteriormente. Puedes iniciar sesión.</p>
                                
                            </div>
                        </body>
                        </html>
                    """)
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponse("""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Error de Verificación</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background-color: #f5f5f5;
                        }
                        .container {
                            text-align: center;
                            padding: 2rem;
                            background-color: white;
                            border-radius: 8px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            max-width: 400px;
                            width: 90%;
                        }
                        .error {
                            color: #dc3545;
                        }
                        .message {
                            margin: 1rem 0;
                            font-size: 1.1rem;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="error">✗ Error de Verificación</h1>
                        <p class="message">El link de verificación es inválido o ha expirado.</p>
                    </div>
                </body>
                </html>
            """)

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