from rest_framework.exceptions import ValidationError

class BusinessFilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        business_id = self.request.query_params.get('business_id') or self.request.data.get('business')
        
        if not business_id:
            raise ValidationError({'business': 'This field is required'})
            
        return queryset.filter(business_id=business_id)

    def perform_create(self, serializer):
        business_id = self.request.data.get('business')
        if not business_id:
            raise ValidationError({'business': 'This field is required'})
        serializer.save(business_id=business_id) 