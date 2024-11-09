from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import License
from django.utils import timezone

class Command(BaseCommand):
    help = 'Crea licencias de prueba de 7 días para todos los usuarios que no tengan una'

    def handle(self, *args, **options):
        users = User.objects.all()
        licenses_created = 0

        for user in users:
            # Verificar si el usuario ya tiene licencia
            if not License.objects.filter(user=user).exists():
                # Crear nueva licencia con 7 días de prueba
                expiration = timezone.now() + timezone.timedelta(days=7)
                License.objects.create(
                    user=user,
                    start_date=timezone.now(),
                    expiration_date=expiration,
                    active=True,
                    notes='Licencia de prueba por 7 días'
                )
                licenses_created += 1
                self.stdout.write(f"Licencia creada para: {user.username}")

        self.stdout.write(
            self.style.SUCCESS(f'Se crearon {licenses_created} licencias nuevas')
        )