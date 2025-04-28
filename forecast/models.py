from django.contrib.auth import get_user_model
from django.db import models

from users.views import User


class WeatherForecast(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        null=True,  # Разрешаем NULL для общих прогнозов
        blank=True
    )
    date = models.DateField(unique=True)
    temp = models.FloatField()
    humidity = models.IntegerField()
    precipitation = models.FloatField()
    location = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.date}: {self.temp}°C"


User = get_user_model()

class WeatherDataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dataset {self.id} by {self.user.email}"