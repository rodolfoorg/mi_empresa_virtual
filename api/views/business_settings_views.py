from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from ..models import BusinessSettings
from ..serializers import BusinessSettingsSerializer

class BusinessSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            print("Usuario actual:", self.request.user)  # Debug
            print("¿Usuario autenticado?", self.request.user.is_authenticated)  # Debug
            
            # Verificar si el usuario tiene un negocio
            if not hasattr(self.request.user, 'business'):
                print("El usuario no tiene un negocio asociado")
                return BusinessSettings.objects.none()
            
            settings = BusinessSettings.objects.filter(business__user=self.request.user)
            print("Configuraciones encontradas:", settings.count())  # Debug
            return settings
            
        except Exception as e:
            print(f"Error detallado en get_queryset: {str(e)}")
            import traceback
            print(traceback.format_exc())  # Imprime el traceback completo
            return BusinessSettings.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            print("Iniciando list")  # Debug
            print("Usuario:", request.user)  # Debug
            
            if not hasattr(request.user, 'business'):
                print("Creando negocio para el usuario")
                from ..models import Business
                business = Business.objects.create(
                    user=request.user,
                    name="Mi Negocio",
                    owner=request.user.username
                )
            else:
                business = request.user.business
                print("Negocio encontrado:", business)  # Debug
            
            settings = self.get_queryset().first()
            print("Settings encontrados:", settings)  # Debug
            
            if not settings:
                print("Creando nueva configuración")  # Debug
                settings = BusinessSettings.objects.create(
                    business=business,
                    theme_color='#4F46E5',
                    secondary_color='#4F46E5',
                    business_hours={
                        "lunes": {"abierto": True, "horario": [{"apertura": "09:00", "cierre": "18:00"}]},
                        "martes": {"abierto": True, "horario": [{"apertura": "09:00", "cierre": "18:00"}]},
                        "miercoles": {"abierto": True, "horario": [{"apertura": "09:00", "cierre": "18:00"}]},
                        "jueves": {"abierto": True, "horario": [{"apertura": "09:00", "cierre": "18:00"}]},
                        "viernes": {"abierto": True, "horario": [{"apertura": "09:00", "cierre": "18:00"}]},
                        "sabado": {"abierto": True, "horario": [{"apertura": "09:00", "cierre": "13:00"}]},
                        "domingo": {"abierto": False, "horario": []}
                    }
                )
            
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
            
        except Exception as e:
            print(f"Error detallado en list: {str(e)}")
            import traceback
            print(traceback.format_exc())  # Imprime el traceback completo
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, 
                data=request.data, 
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            print(f"Error en update: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"Error en destroy: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'])
    def update_theme(self, request, pk=None):
        try:
            instance = self.get_object()
            theme_data = {
                'theme_color': request.data.get('theme_color'),
                'secondary_color': request.data.get('secondary_color'),
                'use_gradient': request.data.get('use_gradient', False)
            }
            serializer = self.get_serializer(
                instance, 
                data=theme_data, 
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            print(f"Error en update_theme: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'])
    def update_social_media(self, request, pk=None):
        try:
            instance = self.get_object()
            social_data = {
                'facebook_url': request.data.get('facebook_url'),
                'instagram_url': request.data.get('instagram_url'),
                'whatsapp_number': request.data.get('whatsapp_number'),
                'telegram_user': request.data.get('telegram_user')
            }
            serializer = self.get_serializer(
                instance, 
                data=social_data, 
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            print(f"Error en update_social_media: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'])
    def update_delivery_settings(self, request, pk=None):
        try:
            instance = self.get_object()
            delivery_data = {
                'does_delivery': request.data.get('does_delivery'),
                'delivery_zones': request.data.get('delivery_zones', {})
            }
            serializer = self.get_serializer(
                instance, 
                data=delivery_data, 
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            print(f"Error en update_delivery_settings: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PublicBusinessSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BusinessSettingsSerializer
    permission_classes = [AllowAny]
    queryset = BusinessSettings.objects.all()