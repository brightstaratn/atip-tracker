from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

class ATIPRequestStatus(models.TextChoices):
    # Comprehensive status choices as previously defined
    DRAFT = 'DRAFT', 'Draft'
    SUBMITTED = 'SUBMITTED', 'Submitted to Institution'
    RECEIVED = 'RECEIVED', 'Response Received'
    REJECTED = 'REJECTED', 'Request Rejected'
    APPEALED = 'APPEALED', 'Appealed to Access Commission'
    CLOSED_COMPLETE = 'CLOSED_COMPLETE', 'Closed - Fully Satisfied'

class ATIPRequest(models.Model):
    # Unique identifier generation
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User who created the request
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Request details
    request_number = models.CharField(max_length=100, unique=True)
    request_text = models.TextField()
    institution = models.CharField(max_length=255)
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=ATIPRequestStatus.choices,
        default=ATIPRequestStatus.DRAFT
    )  # Missing closing parenthesis here
    
    # Deadline tracking
    date_submitted = models.DateField(default=timezone.now)
    response_due_date = models.DateField(null=True, blank=True)
    appeal_deadline = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_deadlines(self):
        """Calculate response and appeal deadlines"""
        from datetime import timedelta
        
        # Initial response deadline (20 working days)
        self.response_due_date = self.date_submitted + timedelta(days=20)
        
        # Appeal deadline (30 days from response or rejection)
        self.appeal_deadline = self.response_due_date + timedelta(days=30)
        
        self.save()

    def save(self, *args, **kwargs):
        # Auto-generate request number if not exists
        if not self.request_number:
            self.request_number = f"ATIP-{self.id}"
        
        # Calculate deadlines on save
        if not self.response_due_date:
            self.calculate_deadlines()
        
        super().save(*args, **kwargs)

class Document(models.Model):
    """Attachments for ATIP requests"""
    request = models.ForeignKey(
        ATIPRequest, 
        related_name='documents', 
        on_delete=models.CASCADE
    )  # Missing closing parenthesis here
    
    file = models.FileField(upload_to='atip_documents/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class StatusTransition(models.Model):
    """Track status changes for each request"""
    request = models.ForeignKey(
        ATIPRequest, 
        related_name='transitions', 
        on_delete=models.CASCADE
    )  # Missing closing parenthesis here
    
    from_status = models.CharField(
        max_length=20,
        choices=ATIPRequestStatus.choices
    )  # Missing closing parenthesis here
    
    to_status = models.CharField(
        max_length=20,
        choices=ATIPRequestStatus.choices
    )  # Missing closing parenthesis here
    
    transition_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
