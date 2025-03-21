import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

df=pd.read_csv("new_app/dataset/Cleaned_dataset.xls")

features = df[['Latitude', 'Longitude', 'Noofvehicle_involved',
                'Severity_Fatal', 'Severity_Grievous Injury', 
                'Weather_Clear', 'Weather_Cloudy', 'Weather_Heavy Rain', 
                'Weather_Light Rain', 'Road_Type_NH', 'Road_Type_Residential Street']]
df=df[features]

scaler=StandardScaler()
features_scaled=scaler.fit_transform(df)


kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(features_scaled)

df.to_csv("prediction/ml_models/clustered_accidents.csv", index=False)

print("Model Training is successfull")
