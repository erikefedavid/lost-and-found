# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.contrib.auth.models import AbstractUser, BaseUserManager
# pyrefly: ignore [missing-import]
from django.utils.translation import gettext_lazy as _
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import re
import django.utils.crypto as crypto

def compress_image(image_field):
    if not image_field:
        return image_field
    
    try:
        img = Image.open(image_field)
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format='JPEG', quality=70)
        output.seek(0)
        
        filename = image_field.name.split('.')[0] + '.jpg'
        
        return InMemoryUploadedFile(
            output, 'ImageField', filename, 'image/jpeg', sys.getsizeof(output), None
        )
    except Exception as e:
        return image_field # Return original if something goes wrong

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    campus_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return self.email

class LostItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lost_items')
    item_name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    date_lost = models.DateField()
    image = models.ImageField(upload_to='lost_items/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from django.core.files.uploadedfile import UploadedFile
        if self.image and isinstance(self.image.file, UploadedFile):
            self.image = compress_image(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.item_name

class FoundItem(models.Model):
    STATUS_CHOICES = (
        ('unclaimed', 'Unclaimed'),
        ('claimed', 'Claimed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='found_items')
    item_name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    date_found = models.DateField()
    image = models.ImageField(upload_to='found_items/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unclaimed')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from django.core.files.uploadedfile import UploadedFile
        if self.image and isinstance(self.image.file, UploadedFile):
            self.image = compress_image(self.image)
            
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # The Auto-Match Brain
            from .models import LostItem, Notification
            
            # Common words to ignore so we don't get false positives
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'my', 'lost', 'found', 'missing', 'black', 'white', 'blue', 'red', 'is', 'was', 'with'}
            
            # Extract meaningful keywords from the found item's name
            raw_words = re.findall(r'\b\w+\b', self.item_name.lower())
            
            # Special case: include short but important campus words like 'ID', 'PC', 'CV'
            important_short_words = {'id', 'pc', 'cv', 'ks'}
            found_keywords = set([w for w in raw_words if (w not in stop_words and len(w) > 2) or w in important_short_words])
            
            if found_keywords:
                # Find lost items in the same category, reported before or on the day this was found
                potential_matches = LostItem.objects.filter(
                    category=self.category,
                    date_lost__lte=self.date_found
                )
                
                for lost_item in potential_matches:
                    lost_words = re.findall(r'\b\w+\b', lost_item.item_name.lower())
                    lost_keywords = set([w for w in lost_words if (w not in stop_words and len(w) > 2) or w in important_short_words])
                    
                    # If there's an intersection in the important keywords, we have a match!
                    if found_keywords.intersection(lost_keywords):
                        Notification.objects.create(
                            user=lost_item.user,
                            title="Potential Match Found! 🔍",
                            message=f"System Alert: Someone just reported a found item ('{self.item_name}') that might match the '{lost_item.item_name}' you lost. Please check the Browse page!"
                        )

    def __str__(self):
        return self.item_name

class Claim(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE, related_name='claims')
    justification = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    claim_token = models.CharField(max_length=10, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            old_status = Claim.objects.get(pk=self.pk).status

        # Generate token if approved
        if self.status == 'approved' and not self.claim_token:
            self.claim_token = f"LCU-{crypto.get_random_string(length=6).upper()}"

        # If the claim is approved, mark the item as claimed
        if self.status == 'approved':
            self.found_item.status = 'claimed'
            self.found_item.save()
            
            # Create notification if status just became approved
            if is_new or old_status != 'approved':
                Notification.objects.create(
                    user=self.user,
                    title="Claim Approved! 🎉",
                    message=f"Great news! Your claim for '{self.found_item.item_name}' has been approved. Your collection code is: {self.claim_token}. Please present this code at the security office."
                )
        
        # If the claim is rejected
        elif self.status == 'rejected':
            if is_new or old_status != 'rejected':
                Notification.objects.create(
                    user=self.user,
                    title="Claim Update",
                    message=f"Your claim for '{self.found_item.item_name}' was not approved. Please contact the security office if you believe this is an error."
                )

        # If it was approved but now it's not (reverted), mark it as unclaimed again
        elif not is_new and old_status == 'approved' and self.status != 'approved':
            other_approved = Claim.objects.filter(found_item=self.found_item, status='approved').exclude(id=self.id).exists()
            if not other_approved:
                self.found_item.status = 'unclaimed'
                self.found_item.save()
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Claim by {self.user.email} for {self.found_item.item_name}"

class AdminLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs')
    action = models.CharField(max_length=300)
    target_type = models.CharField(max_length=100)
    target_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.email} - {self.action} at {self.timestamp}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Trigger real email notification
            from django.core.mail import send_mail
            from django.conf import settings
            
            try:
                subject = f"🔔 {self.title}"
                message = f"Hello {self.user.full_name},\n\nYou have a new notification on the Campus Recovery Hub:\n\n{self.message}\n\nCheck your dashboard for more details.\n\nBest regards,\nCampus Recovery Team"
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                pass # Don't crash if email fails

    def __str__(self):
        return f"Notification for {self.user.email}: {self.title}"
