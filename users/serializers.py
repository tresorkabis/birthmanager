from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    username = None
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2= serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ( 'email', 'password', 'password2','noms', )
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'noms': {'required': True, 'allow_blank': False},
           ' password':{'write_only': True, 'required': True, 'validators': [validate_password]},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Les deux mots de passe ne sont pas similaires")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta :
        model = User
        fields = ('noms', 'profile_picture')
        read_only_fields = ('id','email','created_at','updated_at')
        
    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        return user

