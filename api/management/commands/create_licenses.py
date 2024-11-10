from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import License
from django.utils import timezone

class Command(BaseCommand):
    help = 'Elimina todas las licencias existentes y crea nuevas licencias básicas de prueba de 7 días'

    def handle(self, *args, **options):
        # Eliminar todas las licencias existentes
        License.objects.all().delete()
        self.stdout.write("Se eliminaron todas las licencias existentes")

        users = User.objects.all()
        licenses_created = 0

        for user in users:
            # Crear nueva licencia básica con 7 días de prueba
            expiration = timezone.now() + timezone.timedelta(days=7)
            License.objects.create(
                user=user,
                plan='basico',
                start_date=timezone.now(),
                expiration_date=expiration,
                active=True,
                notes='Licencia básica de prueba por 7 días'
            )
            licenses_created += 1
            self.stdout.write(f"Licencia básica creada para: {user.username}")

        self.stdout.write(
            self.style.SUCCESS(f'Se crearon {licenses_created} licencias básicas nuevas')
        )