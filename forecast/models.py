from django.db import models


class WeatherForecast(models.Model):
    date = models.DateField(unique=True)
    temp = models.FloatField()
    humidity = models.IntegerField()
    precipitation = models.FloatField()
    location = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.date}: {self.temp}°C"