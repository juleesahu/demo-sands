from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from users.managers import CustomUserManager
from django.db.models.signals import post_save
from django.conf import settings
from django.apps import apps  # ✅ Fix circular import
import random

# Custom User model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email', unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    unique_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    referral_code = models.CharField(max_length=100, blank=True, null=True)

    # Referral System
    parent_sponsor = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='sponsored_users'
    )
    parent_node = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='child_nodes'
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def generate_unique_id(self):
        """Generate a unique ID in the format: VGS-SS-FL-XXXXXXXXXX"""
        company_name = "VGS"
        product_name = "SS"
        first_initial = self.first_name[0].upper() if self.first_name else 'X'
        last_initial = self.last_name[0].upper() if self.last_name else 'X'
        random_number = random.randint(1000000000, 9999999999)
        unique_id = f"{company_name}-{product_name}-{first_initial}{last_initial}-{random_number}"

        # Ensure uniqueness
        while CustomUser.objects.filter(unique_id=unique_id).exists():
            random_number = random.randint(1000000000, 9999999999)
            unique_id = f"{company_name}-{product_name}-{first_initial}{last_initial}-{random_number}"

        return unique_id

    def save(self, *args, **kwargs):
        """Ensure unique_id is generated before saving"""
        if not self.unique_id:
            self.unique_id = self.generate_unique_id()
        super().save(*args, **kwargs)

    def get_referral_link(self):
        """Generates the referral link containing the user's unique ID."""
        base_url = settings.FRONTEND_URL  # Example: "https://myapp.com"
        return f"{base_url}/users/register?ref={self.unique_id}"

    @property
    def referred_by(self):
        """Returns the email of the parent_sponsor (referrer)."""
        return self.parent_sponsor.email if self.parent_sponsor else "Company"

    @property
    def placed_under(self):
        """Returns the email of the parent_node (hierarchical placement)."""
        return self.parent_node.email if self.parent_node else "Company"

# Profile model
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/products', null=True, blank=True, default='default/pic.png')
    date_modified = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'User Profile'

# Shipping Address model
class ShippingAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Shipping Addresses"

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'

def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create user profile, assign parent sponsor & parent node, and insert into MLMTree."""
    if created:
        Profile.objects.create(user=instance)
        MLMTree = apps.get_model('mlmtree', 'MLMTree')

        if instance.is_superuser:
            instance.parent_sponsor = None
            instance.parent_node = None
            instance.save()
            MLMTree.objects.create(user=instance, parent=None)
            return

        if not instance.parent_sponsor:
            company_user = CustomUser.objects.filter(is_superuser=True).first()
            instance.parent_sponsor = company_user

        if not instance.parent_node:
            sponsor = instance.parent_sponsor
            if sponsor:
                children = sponsor.child_nodes.all()
                if children.count() < 5:
                    instance.parent_node = sponsor
                else:
                    queue = list(children)
                    while queue:
                        potential_parent = queue.pop(0)
                        if potential_parent.child_nodes.count() < 5:
                            instance.parent_node = potential_parent
                            break
                        queue.extend(potential_parent.child_nodes.all())

        instance.save()

        if instance.parent_node and not hasattr(instance.parent_node, 'mlm_tree'):
            MLMTree.objects.create(user=instance.parent_node, parent=instance.parent_node.parent_node.mlm_tree if instance.parent_node.parent_node else None)

        MLMTree.objects.create(user=instance, parent=instance.parent_node.mlm_tree if instance.parent_node else None)

post_save.connect(create_user_profile, sender=CustomUser)