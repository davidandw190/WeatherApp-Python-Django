from django.shortcuts import render
import requests
import datetime
import geocoder


def get_lat_lon(city):
    geolocation = geocoder.osm(city)
    if geolocation.ok:
        return geolocation.lat, geolocation.lng
    else:
        return None, None


def fetch_weather_and_forecast(lat, lon, api_key, current_weather_url, forecast_url):

    current_weather_response = requests.get(current_weather_url.format(lat, lon, api_key)).json()

    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()

    weather_data = {
        'city': forecast_response['city']['name'],
        'temperature': int(round(current_weather_response['main']['temp'] - 273.15, 0)),
        'description': current_weather_response['weather'][0]['description'],
        'icon': current_weather_response['weather'][0]['icon'],
        'precipitation': int((forecast_response['list'][0]['pop']) * 100),
        'cloudiness': forecast_response['list'][0]['clouds']['all'],
    }

    displayed_forecasts = []
    for forecast in forecast_response['list'][:10]:
        forecast_datetime = datetime.datetime.fromtimestamp(forecast['dt'])
        day_hour = forecast_datetime.strftime('%A %H:%M')
        displayed_forecasts.append({
            'datetime': day_hour,
            'temperature': {
                'min': int(round(forecast['main']['temp_min'] - 273.15, 0)),
                'max': int(round(forecast['main']['temp_max'] - 273.15, 0))
            },
            'feels_like': int(round(forecast['main']['feels_like'] - 273.15, 0)),
            'description': forecast['weather'][0]['description'],
            'icon': forecast['weather'][0]['icon'],
        })

    return weather_data, displayed_forecasts


def index(request):
    api_key = ''
    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}'

    if request.method == 'POST':
        city1 = request.POST['city1']
        city2 = request.POST.get('city2', None)

        lat1, lon1 = get_lat_lon(city1)
        weather_data1, displayed_forecasts1 = fetch_weather_and_forecast(lat1, lon1, api_key, current_weather_url, forecast_url)

        if city2:
            lat2, lon2 = get_lat_lon(city2)
            weather_data2, displayed_forecasts2 = fetch_weather_and_forecast(lat2, lon2, api_key, current_weather_url, forecast_url)
        else:
            weather_data2, displayed_forecasts2 = None, None

        context = {
            'weather_data1': weather_data1,
            'displayed_forecasts1': displayed_forecasts1,
            'weather_data2': weather_data2,
            'displayed_forecasts2': displayed_forecasts2,
        }

        return render(request, 'weather_app/index.html', context)
    else:
        return render(request, 'weather_app/index.html')
