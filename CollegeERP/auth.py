from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from info.models import User
import logging

logger = logging.getLogger(__name__)

class KeycloakOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """Custom authentication backend to integrate Keycloak with Django."""
    
    def create_user(self, claims):
        """Create a new user from Keycloak claims."""
        logger.info(f"Creating new user from Keycloak claims: {claims.get('preferred_username')}")
        
        # Extract user information from claims
        username = claims.get('preferred_username', '')
        email = claims.get('email', '')
        first_name = claims.get('given_name', '')
        last_name = claims.get('family_name', '')
        
        # Create the user - adjust fields as needed for your custom User model
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        # Update user with additional information
        self.update_user(user, claims)
        return user

    def update_user(self, user, claims):
        """Update existing user with new claims."""
        logger.info(f"Updating user from Keycloak claims: {user.username}")
        
        # Update basic user information
        user.first_name = claims.get('given_name', user.first_name)
        user.last_name = claims.get('family_name', user.last_name)
        user.email = claims.get('email', user.email)
        
        # Map Keycloak roles to Django permissions
        if 'realm_access' in claims and 'roles' in claims['realm_access']:
            roles = claims['realm_access']['roles']
            logger.info(f"User roles from Keycloak: {roles}")
            
            # Reset permissions first to ensure clean state
            user.is_staff = False
            user.is_superuser = False
            
            # Map app-specific roles to Django permissions
            if 'app-admin' in roles:
                user.is_staff = True
                user.is_superuser = True
                logger.info(f"User {user.username} granted admin permissions")
            elif 'app-view' in roles:
                user.is_staff = True
                user.is_superuser = False
                logger.info(f"User {user.username} granted view-only permissions")
            
        user.save()
        return user

    def filter_users_by_claims(self, claims):
        """Match users by username from Keycloak."""
        username = claims.get('preferred_username')
        if not username:
            return User.objects.none()
        
        # Try to find existing user
        users = User.objects.filter(username=username)
        logger.info(f"Found {users.count()} users matching username: {username}")
        return users

    def verify_claims(self, claims):
        """Verify the provided claims to decide if authentication should be allowed."""
        # Verify that required claims are present
        verified = super().verify_claims(claims)
        
        # Add additional verification if needed
        # For example, you might want to check for specific roles or attributes
        
        return verified
