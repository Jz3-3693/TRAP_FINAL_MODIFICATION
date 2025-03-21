from http.client import HTTPResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from .models import contact
import numpy as np
import joblib
from.models import AccidentPrediction
import folium

#load pickle files

kmeans=joblib.load("new_app/dataset/kmeans_model_cldtst.pkl")
scaler=joblib.load("new_app/dataset/kmeans_scaler_cldtst.pkl")

# Login page view
def login(request):
    return render(request, 'login.html')

# Home page view
def home(request):
    return render(request, 'home.html')

# Index page view
def index(request):
    return render(request, 'index.html')
def result(request):
    return render(request, 'result.html')


# Register view
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('rusnm')
        email = request.POST.get('remail')
        password = request.POST.get('regpass')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register_view')
        else:
            # Create user and save to db
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Account successfully created. Please login!')
            return redirect('login_view')
    
    return render(request, 'login.html', {'form_type': 'register'})

# Login view
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
       

        # Authenticate User
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Incorrect username or password')
    
    return render(request, 'login.html', {'form_type': 'login'})


# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out')
    return redirect('home')
#contact Us view
def contact_us(request):
    if request.method == 'POST':
       if request.POST.get('form_type') == 'contact_view':
    
         email = request.POST.get('email')
         name = request.POST.get('name')
         message = request.POST.get('message')
         if not name or not email or not message:
             messages.error(request,'Please fill all filds')
         else:
            info=contact.objects.create(name=name, email=email, message=message)
            info.save()
            messages.success(request, 'Message uploaded')
            return redirect('contact_us') 
    return render(request, 'home.html')


  


from django.contrib.auth.decorators import login_required
import numpy as np
from django.shortcuts import render
from .models import AccidentPrediction

@login_required  # Ensure only logged-in users can predict
def predict_future_hotspot(request):
    context = {"cluster": None, "latitude": None, "longitude": None}

    if request.method == "POST":
        latitude = float(request.POST.get("latitude"))
        longitude = float(request.POST.get("longitude"))
        no_of_vehicles = int(request.POST.get("no_of_vehicles"))

        severity_fatal = int(request.POST.get("severity_fatal"))
        severity_grievous = int(request.POST.get("severity_grievous"))

        road_type_nh = int(request.POST.get("road_type_nh"))
        road_type_residential = int(request.POST.get("road_type_residential"))

        weather_clear = int(request.POST.get("weather_clear"))
        weather_cloudy = int(request.POST.get("weather_cloudy"))
        weather_heavy_rain = int(request.POST.get("weather_heavy_rain"))
        weather_light_rain = int(request.POST.get("weather_light_rain"))

        # Prepare input data
        new_input = np.array([[latitude, longitude, no_of_vehicles, severity_fatal, 
                               severity_grievous, road_type_nh, road_type_residential, 
                               weather_clear, weather_cloudy, weather_heavy_rain, weather_light_rain]])

        # Scale the input data
        new_input_scaled = scaler.transform(new_input)

        # Predict the cluster
        predicted_cluster = kmeans.predict(new_input_scaled)[0]

        # Save the prediction linked to the logged-in user
        hotspot = AccidentPrediction(
            user=request.user,  # Save under the current user
            latitude=latitude, 
            longitude=longitude, 
            cluster=predicted_cluster
        )
        hotspot.save()

        # Update context to show results
        context.update({"cluster": predicted_cluster, "latitude": latitude, "longitude": longitude})

    return render(request, "index.html", context)


@login_required
def map_view(request):
    """
    View to display the predicted accident hotspot on a separate map page.
    """
    latitude = request.GET.get("latitude")
    longitude = request.GET.get("longitude")
    cluster = request.GET.get("cluster")  

    if not latitude or not longitude:
        return HttpResponse("Latitude and Longitude are required.", status=400)

    # Get only past hotspots for the logged-in user
    past_hotspots = AccidentPrediction.objects.filter(user=request.user).exclude(latitude=latitude, longitude=longitude)

    return render(request, "result.html", {
        "latitude": latitude,
        "longitude": longitude,
        "cluster": cluster,
        "past_hotspots": past_hotspots
    })


import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import urllib, base64
from django.shortcuts import render
from .models import AccidentPrediction

def get_graph():
    """Converts Matplotlib figure into a base64-encoded string to display in Django template."""
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    graph = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    return f"data:image/png;base64,{graph}"

def visualization_view(request):
    # Fetch accident data
    accidents = AccidentPrediction.objects.all()

    # Convert to DataFrame
    data = pd.DataFrame(list(accidents.values("timestamp", "cluster", "latitude", "longitude")))

    # Convert timestamp to datetime
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data["hour"] = data["timestamp"].dt.hour
    data["date"] = data["timestamp"].dt.date

    # ---- 1️⃣ Heatmap of Accident Locations ----
    plt.figure(figsize=(8, 6))
    sns.kdeplot(x=data["longitude"], y=data["latitude"], cmap="Reds", fill=True)
    plt.scatter(data["longitude"], data["latitude"], alpha=0.3, color="blue", label="Accident Locations")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Geographical Heatmap of Accidents")
    plt.legend()
    heatmap_graph = get_graph()

    # ---- 2️⃣ Scatter Plot of Accident Clusters ----
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=data["longitude"], y=data["latitude"], hue=data["cluster"], palette="viridis", alpha=0.7)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Accident Clusters Based on Location")
    scatter_graph = get_graph()

    # ---- 3️⃣ Accident Frequency Over Time ----
    plt.figure(figsize=(10, 8))
    data["date"].value_counts().sort_index().plot(kind="line", marker="o", color="blue")
    plt.xlabel("Date")
    plt.ylabel("Number of Accidents")
    plt.title("Accident Frequency Over Time")
    plt.grid(True)
    time_trend_graph = get_graph()

    # ---- 4️⃣ Accidents by Hour of Day ----
    plt.figure(figsize=(10, 6))
    sns.histplot(data["hour"], bins=24, kde=True, color="green")
    plt.xlabel("Hour of Day")
    plt.ylabel("Accident Count")
    plt.title("Accident Occurrences by Hour")
    plt.grid(True)
    hourly_trend_graph = get_graph()

    return render(request, "visualization.html", {
        "heatmap_graph": heatmap_graph,
        # "scatter_graph": scatter_graph,
        "time_trend_graph": time_trend_graph,
        "hourly_trend_graph": hourly_trend_graph
    })
    from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.save()
        return redirect('profile')