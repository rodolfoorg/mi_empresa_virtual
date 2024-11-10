from rest_framework import viewsets
from ..models import Contact
from ..serializers import ContactSerializer
from ..mixins import BusinessFilterMixin

class ContactViewSet(BusinessFilterMixin, viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    queryset = Contact.objects.none()

    def get_queryset(self):
        return Contact.objects.filter(business=self.request.user.business)