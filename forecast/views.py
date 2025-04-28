from dataclasses import replace

from django.shortcuts import redirect
from .models import WeatherForecast
from .forms import DatasetUploadForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import datetime, timedelta
import random

from .utils import process_weather_data


@login_required(login_url='/login/')  # Редирект на страницу входа
def index(request):
    # Генерируем тестовые данные (в реальном приложении замените на API погоды)
    today = datetime.now().date()
    weather_data = []

    # Получаем последние 6 дней данных
    latest_date = WeatherForecast.objects.filter(user=request.user).latest('date').date
    start_date = latest_date - timedelta(days=7)

    data = WeatherForecast.objects.filter(
        user=request.user,
        date__range=[start_date, latest_date + timedelta(days=7)]
    ).order_by('date')

    # Подготовка данных для графика
    dates = [d.date.strftime("%d.%m") for d in data]
    temps = [d.temp for d in data]

    for i in range(7):
        date = today + timedelta(days=i)
        weather_data.append({
            'date': date,
            'temp': temps[i],
            'humidity': random.randint(40, 90),
            'precipitation': random.randint(0, 10),
        })

    return render(request, 'weather/index.html', {'weather_data': weather_data})



@login_required
def upload_dataset(request):
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.user = request.user
            dataset.save()

            # Обработка файла
            process_weather_data(dataset.file.path, request.user)
            return redirect('/')
    else:
        form = DatasetUploadForm()
    return render(request, 'weather/upload.html', {'form': form})


@login_required
def statistics_view(request):
    # Получаем последнюю дату в данных
    last_date = WeatherForecast.objects.order_by('-date').first().date
    today = last_date

    # Данные за последние 6 дней
    past_data = WeatherForecast.objects.filter(
        date__gte=today - timedelta(days=6),
        date__lt=today
    ).order_by('date')

    # Прогноз на следующие 6 дней
    forecast_data = WeatherForecast.objects.filter(
        date__gte=today + timedelta(days=1),
        date__lt=today + timedelta(days=7)
    ).order_by('date')

    # Подготовка данных для графика
    dates = []
    temperatures = []
    pressures = []

    for data in past_data:
        dates.append(data.date.strftime('%Y-%m-%d %H:%M'))
        temperatures.append(data.temp)

    for data in forecast_data:
        if data.forecast_date.strftime('%Y-%m-%d %H:%M') not in dates:
            dates.append(str(data.forecast_date.strftime('%Y-%m-%d %H:%M')))
            temperatures.append(data.temperature)
            pressures.append(data.pressure)

    context = {
        "dates": str(dates).replace("'", '"'),
        "temperatures": temperatures,
        "today": today.strftime('%Y-%m-%d %H:%M')
    }

    print(forecast_data)

    return render(request, 'weather/statistics.html', context)