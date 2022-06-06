from sklearn.preprocessing import minmax_scale, StandardScaler
import numpy as np

data = [1,2,3,4,5]

print(minmax_scale(data))

scaler = StandardScaler()

data_to_norm = np.array(data).reshape(-1,1)
print(scaler.fit_transform(data_to_norm))
