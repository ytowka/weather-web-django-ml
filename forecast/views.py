from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import datetime, timedelta
import random

@login_required(login_url='/login/')  # Редирект на страницу входа
def index(request):
    # Генерируем тестовые данные (в реальном приложении замените на API погоды)
    today = datetime.now().date()
    weather_data = []

    for i in range(7):
        date = today + timedelta(days=i)
        weather_data.append({
            'date': date,
            'temp': random.randint(15, 25),
            'humidity': random.randint(40, 90),
            'precipitation': random.randint(0, 10),
        })

    return render(request, 'weather/index.html', {'weather_data': weather_data})