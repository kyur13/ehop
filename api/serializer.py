from rest_framework import serializers
from .models import contactus
class contactserializer(serializers.ModelSerializer):
    class Meta:
        model=contactus
        fields='__all__'