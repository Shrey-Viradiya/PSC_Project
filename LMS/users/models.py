from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Member(models.Model):
    MEMBER_TYPE_CHOICES = [
        ('BTECH', 'Bachelor'),
        ('MTECH', 'Master'),
        ('_PhD_', 'Doctorate'),
        ('FCLT_', 'Faculty'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    memberType = models.CharField(max_length=5, choices=MEMBER_TYPE_CHOICES, default='BTECH')
    address = models.TextField(null=True)
    contact = PhoneNumberField(null=True, blank=True, unique=True)
    expiry_date = models.DateTimeField(default=datetime.now() + timedelta(days=365))
    fine = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} __MemberType {self.memberType}"
