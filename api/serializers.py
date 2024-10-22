from rest_framework import serializers
from api.models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'  

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'  

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'  

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'  

class CashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cash
        fields = '__all__'  

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'  

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'  