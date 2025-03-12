from rest_framework import serializers

class Loginserial(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField()