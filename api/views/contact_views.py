from rest_framework import viewsets
from ..models import Contact
from ..mixins import BusinessFilterMixin
from ..serializers import ContactSerializer

class ContactViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet para manejar contactos
    """
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()