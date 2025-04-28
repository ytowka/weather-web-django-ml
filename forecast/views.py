import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import WeatherForecast, WeatherDataset
from .forms import DatasetUploadForm
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import datetime, timedelta
import random

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
            process_dataset(dataset.file.path, request.user)
            return redirect('/')
    else:
        form = DatasetUploadForm()
    return render(request, 'weather/upload.html', {'form': form})


def process_dataset(file_path, user):
    # Чтение и подготовка данных
    df = pd.read_csv(
        file_path,
        sep=';',
        parse_dates=['Местное время'],
        dayfirst=True,
        usecols=['Местное время', 'T', 'P', 'U', 'WW']
    )

    # Переименование колонок
    df.columns = ['datetime', 'temp', 'pressure', 'humidity', 'precipitation']

    # Очистка данных
    df = df.dropna()
    df['date'] = df['datetime'].dt.date

    # Находим последнюю дату
    latest_date = df['date'].max()

    # Подготовка данных для модели
    features = df[['temp', 'pressure', 'humidity']]
    target_temp = df['temp']
    target_pressure = df['pressure']

    # Обучение моделей
    model_temp = RandomForestRegressor()
    model_pressure = RandomForestRegressor()

    model_temp.fit(features, target_temp)
    model_pressure.fit(features, target_pressure)

    # Прогноз на 6 дней
    forecast_dates = [latest_date + timedelta(days=i) for i in range(0, 7)]
    forecasts = []

    for date in forecast_dates:
        # Генерация прогноза (упрощенный пример)
        forecast = {
            'date': date,
            'temp': model_temp.predict([[10, 750, 70]])[0],
            'pressure': model_pressure.predict([[10, 750, 70]])[0],
            'humidity': 70,
            'precipitation': 0
        }
        forecasts.append(forecast)

        # Сохранение в БД
        WeatherForecast.objects.update_or_create(
            user=user,
            date=date,
            defaults={
                'temp': forecast['temp'],
                'humidity': forecast['humidity'],
                'precipitation': forecast['precipitation'],
                'location': 'custom'
            }
        )


@login_required
def statistics_view(request):
    # Получаем последние 6 дней данных
    latest_date = WeatherForecast.objects.filter(user=request.user).latest('date').date
    start_date = latest_date - timedelta(days=6)

    data = WeatherForecast.objects.filter(
        user=request.user,
        date__range=[start_date, latest_date + timedelta(days=6)]
    ).order_by('date')

    # Подготовка данных для графика
    dates = [d.date.strftime("%d.%m") for d in data]
    temps = [d.temp for d in data]

    return render(request, 'weather/statistics.html', {
        'dates': dates,
        'temps': temps,
        'forecast_temps': [None, None, ..., 18.3, 17.8, ...],  # None для прошлого, значения для прогноза
        'forecast_pressures': [None, None, ..., 755, 753, ...],
        'max_temp': '',
        'min_temp': '',
    })