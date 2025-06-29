from django.db import IntegrityError
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from allauth.account.models import EmailConfirmationHMAC, EmailAddress
from django.utils import timezone
from .serializers import (
UserRegistrationSerializer,
UserUpdateSerializer
)


User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Email invalide'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if not user.check_password(password):
            return Response({'error': 'Mot de passe invalide '}, status=status.HTTP_401_UNAUTHORIZED)
            
        # Check if email is verified (add this field to your model if needed)
        if hasattr(user, 'email_verified') and not user.email_verified:
            return Response({
                'error': 'Verifiez votre email avant de vous connecter',
                'needs_verification': True
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            #user_data = UserProfileSerializer(user).data
            #response.data['user'] = user_data
            
            # Rember to update last login
            user.last_login = timezone.now()
            user.save()
            
        return response

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle registration"""
        serializer = UserRegistrationSerializer(data=request.data)
        print(request.data)
        print(serializer)
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                # Send verification email
                self.send_verification_email(user)
                
                return Response({
                    'message': 'Enregistrement réussi. Verifiez votre bôite mail svp.',
                    'user_id': user.id,
                    'email': user.email
                }, status=status.HTTP_201_CREATED)
                
            except IntegrityError:
                return Response({
                    'error': 'Cet email existe déjà.',
                    'email': ['Cet email existe déjà.']
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'error': "Echec d'enregistrement."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_verification_email(self, user):
        """Send email verification using django-allauth"""
        try:
            email_address = EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False
            )
            
            # Create confirmation and get key
            confirmation = EmailConfirmationHMAC(email_address)
            
            # Build activation URL
            activation_url = '{}/verify-email/{}'.format(
                getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
                confirmation.key
            )
            
            activation_key = confirmation.key
        
            # if settings.DEBUG:
            #     print(f"=== EMAIL VERIFICATION URL ===")
            #     print(f"User: {user.email}")
            #     print(f"Verification URL: {activation_url}")
            #     print(f"================================")
            #     return
                
            # Send email
            
            subject = "Verification de votre compte"
            message = render_to_string('email_verification.html', {
                'user': user,
                'activation_url': activation_url,
                'activation_key': activation_key,
                'expiry_days': getattr(settings, 'EMAIL_CONFIRMATION_EXPIRE_DAYS', 1),
            })
            
            email = EmailMessage(subject, message, to=[user.email])
            email.content_subtype = "html"
            email.send()
            
        except Exception as e:
            # Log the error but don't fail registration
            print(f"Failed to send verification email: {e}")
            import traceback
            traceback.print_exc()

class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, key):
        try:
            confirmation = EmailConfirmationHMAC.from_key(key)
            if not confirmation :
                return Response({'error': 'Clé de vérification expirée.'}, status=status.HTTP_400_BAD_REQUEST)

            
            email_address = confirmation.email_address      
           
            
            if email_address.verified:
                return Response({'message': 'Cet email est déjà verifié'}, status=status.HTTP_200_OK)
            
            confirmed  = confirmation.confirm(request)
            if not confirmed:
                return Response({'error': 'Clé de verification expirée'}, status=status.HTTP_400_BAD_REQUEST)
            
            email_address.refresh_from_db()
            
            # Update user profile - Make sure this field exists in your User model
            user = email_address.user
            if hasattr(user, 'email_verified'):
                user.email_verified = True
                user.save()
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Email vérifié avec succès',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class ResendVerificationView(APIView):
    """Resend email verification"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email est obligatoire'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            # Check if already verified
            if hasattr(user, 'email_verified') and user.email_verified:
                return Response({
                    'message': 'Email déjà vérifié'
                }, status=status.HTTP_200_OK)
            
            # Resend verification email
            self.send_verification_email(user)
            
            return Response({
                'message': 'Email de vérification envoyé avec succès'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': "Utilisateur avec et email n'xiste pas"
            }, status=status.HTTP_404_NOT_FOUND)
    
    def send_verification_email(self, user):
        """Send email verification using django-allauth"""
        try:
            email_address = EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False
            )
            
            confirmation = EmailConfirmationHMAC(email_address)
            
            activation_url = '{}/verify-email/{}'.format(
                getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
                confirmation.key
            )
            
            activation_key = confirmation.key
            
            
            subject = "Verificaion de votre compte"
            message = render_to_string('email_verification.html', {
                'user': user,
                'activation_url': activation_url,
                'activation_key' :  activation_key,
                'expiry_days': getattr(settings, 'EMAIL_CONFIRMATION_EXPIRE_DAYS', 1),
            })
            
            email = EmailMessage(subject, message, to=[user.email])
            email.content_subtype = "html"
            email.send()
            
        except Exception as e:
            print(f"Echec d'envoie de email de vérification: {e}")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Déconnexion réussie.'})
    except Exception as e:
        return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

