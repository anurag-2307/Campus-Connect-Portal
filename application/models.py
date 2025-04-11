from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser

# Club model representing the club itself
class Club(models.Model):
    club_name = models.CharField(max_length=255, unique=True)
    club_email = models.EmailField(max_length=60, unique=True)
    club_desc = models.TextField()
    club_password = models.CharField(max_length=255, blank=True) 
    membership_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    def __str__(self):
        return self.club_name
    def set_password(self, raw_password):
        self.club_password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.club_password)

# CustomUser model representing the user itself
class CustomUser(AbstractUser):
    # We use AbstractUser to extend the built-in Django user model.
    is_club_admin = models.BooleanField(default=False)
    
    # Override these to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',
        blank=True
    )
    
    # ManyToMany relationships
    clubs = models.ManyToManyField(Club, related_name="members")  # Clubs this user belongs to
    events = models.ManyToManyField('Event', related_name='registrants', through='EventRegistration')  # Events the user is part of

    def __str__(self):
        return self.username

# ClubAdmin model, where authentication happens using the club_email
#ClubAdmin model for multiple admins => multiple clubs
'''class ClubAdmin(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='clubadmins')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="admins")
    club_password = models.CharField(max_length=255)  # Store password securely for club login'''

#ClubAdmin Model for one admin => one club, but one club => many admins
class ClubAdmin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='clubadmin')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="admins")
    club_password = models.CharField(max_length=255)  # Store hashed password securely

    class Meta:
        unique_together = ('user', 'club')
    def set_password(self, raw_password):
        self.club_password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.club_password)

    def __str__(self):
        return f"{self.club.club_name} Admin"

# Event model to represent the events created by ClubAdmin
class Event(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="events")
    event_name = models.CharField(max_length=255)
    event_desc = models.TextField()
    event_date = models.DateTimeField()
    event_location = models.CharField(max_length=255)
    event_image = models.ImageField(upload_to='event_images/', blank= True, null= True)
    registration_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    standard_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    member_discount_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return self.event_name
    
class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='event_images/')


# Intermediate model to represent user registrations for events
class EventRegistration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Use CustomUser for registration
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')  # Ensure a user can only register for an event once

    def __str__(self):
        return f'{self.user.username} registered for {self.event.event_name}'
    
# models.p
from django.conf import settings

class VirtualPayment(models.Model):
    PAYMENT_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    paid_on = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        target = self.event.event_name if self.event else self.club.club_name
        return f"Payment by {self.user.username} for {target} [{self.transaction_id}]"

