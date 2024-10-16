# -*- coding: utf-8 -*-
"""SynthesizdData_with GenAI_ZG.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gFjEYR4hrO9TgJsbNKx8mWtYspOGl3x3

# **Importing the Dataset**
"""

import numpy as np
import pandas as pd

# Importing neural network modules
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, BatchNormalization, LeakyReLU, Dropout
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.initializers import RandomNormal
# Importing some machine learning modules
from sklearn.utils import shuffle
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
# Import data visualization modules
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

print("Modules are imported!")

#Dataset can be downloaded from https://data.world/raghu543/credit-card-fraud-data
data = pd.read_csv('creditcard.csv')
data.head()

data.shape

data.Class.value_counts()



"""# **Data Preprocessing and Exploration**"""

#Removing all the rows with Nan values
data.dropna(inplace=True)
data.shape

#Removing Time column
data = data.drop(axis=1, columns='Time')
data.head()

data.shape

#Feature Scaling Amount column
sc = StandardScaler()
data['Amount'] = sc.fit_transform(data[['Amount']]) # Pass Amount as a DataFramed
data.head() # Check the data

#Split the data into features and labels
data_fraud = data[data['Class'] == 1]
data_genuine = data[data['Class'] == 0]
data_fraud.shape, data_genuine.shape

data_fraud

data_genuine

#Split the data into features and labels
X = data.drop(axis=1, columns='Class')
y = data['Class']

#Apply PCA to reduce the dimensionality of features `X` into two dimensions
pca = PCA(n_components=2)
transformed_data = pca.fit_transform(X)
df =pd.DataFrame(data=transformed_data)
df['labels'] = y
df

#use a scatter plot to visualize data
px.scatter(df, x=0, y=1, color=df.labels.astype(str))

"""# **Building the Generator Model**"""

#Write a function to create the Generator model architecture
def build_generator():
  model = Sequential()

  model.add(Dense(32,activation='relu', input_dim=29, kernel_initializer='he_uniform'))
  model.add(BatchNormalization())

  model.add(Dense(64,activation='relu'))
  model.add(BatchNormalization())

  model.add(Dense(128,activation='relu'))
  model.add(BatchNormalization())

  model.add(Dense(29,activation='linear')) # replace relu with linear
  model.summary()

  return model

build_generator()

"""# **Building the Discriminator Model¶**"""

#Write a function to create the Discriminator model architecture
def build_discriminator():
  model = Sequential()

  model.add(Dense(128,activation='relu', input_dim=29, kernel_initializer='he_uniform'))


  model.add(Dense(64,activation='relu'))
  model.add(Dense(32,activation='relu'))
  model.add(Dense(32,activation='relu'))
  model.add(Dense(16,activation='relu'))
  model.add(Dense(1,activation='sigmoid'))
  model.compile(loss='binary_crossentropy', optimizer='adam')


  model.summary()

  return model

build_discriminator()

"""# **Combine Generator and Discriminator models to Build The GAN**

"""

def build_gan(generator, discriminator):
    discriminator.trainable = False
    gan_input = Input(shape=(generator.input_shape[1],))
    x = generator(gan_input)

    gan_output = discriminator(x)
    gan = Model(inputs=gan_input, outputs=gan_output)
    gan.summary()
    return gan

def generate_synthetic_data(generator, num_samples):
    noise = np.random.normal(0, 1, (num_samples, generator.input_shape[1]))
    fake_data = generator.predict(noise)
    return fake_data

"""# **Train and evaluate our GAN**"""

def monitor_generator(generator):
    # Initialize a PCA (Principal Component Analysis) object with 2 components
    pca = PCA(n_components=2)

    # Drop the 'Class' column from the fraud dataset to get real data
    real_fraud_data = data_fraud.drop("Class", axis=1)

    # Transform the real fraud data using PCA
    transformed_data_real = pca.fit_transform(real_fraud_data.values)

    # Create a DataFrame for the transformed real data and add a 'label' column with the value 'real'
    df_real = pd.DataFrame(transformed_data_real)
    df_real['labels'] = "real"

    # Generate synthetic fraud data using the provided generator and specify the number of samples (492 in this case)
    synthetic_fraud_data = generate_synthetic_data(generator, 492)

    # Transform the synthetic fraud data using PCA
    transformed_data_fake = pca.fit_transform(synthetic_fraud_data)

    # Create a DataFrame for the transformed fake data and add a 'label' column with the value 'fake'
    df_fake = pd.DataFrame(transformed_data_fake)
    df_fake['labels'] = "fake"

    # Concatenate the real and fake data DataFrames
    df_combined = pd.concat([df_real, df_fake])

    # Create a scatterplot to visualize the data points, using the first and second PCA components as x and y, respectively,
    # and color points based on the 'label' column, with a size of 10
    plt.figure()
    sns.scatterplot(data=df_combined, x=0, y=1, hue='labels', s=10)
    plt.show()

generator = build_generator()
discriminator = build_discriminator()
gan = build_gan(generator, discriminator)
gan.compile(loss='binary_crossentropy', optimizer='adam')

num_epochs = 100
batch_size = 32
half_batch = int(batch_size/2)

for epoch in range(num_epochs):

    X_fake = generate_synthetic_data(generator, half_batch)
    y_fake = np.zeros((half_batch, 1))

    X_real = data_fraud.drop("Class", axis=1).sample(half_batch)
    y_real = np.ones((half_batch, 1))

    discriminator.trainable = True
    discriminator.train_on_batch(X_real, y_real)
    discriminator.train_on_batch(X_fake, y_fake)


    noise = np.random.normal(0, 1, (batch_size, 29))
    gan.train_on_batch(noise,np.ones((batch_size, 1)))

    if epoch % 10 == 0:
        monitor_generator(generator)

"""# **Generate synthetic data using the trained Generator**"""

#Generate 1000 fradulent data points using the trained generator
synthetic_data = generate_synthetic_data(generator, 500)
df=pd.DataFrame(synthetic_data)
df['labels'] = 'fake'

df2= data_fraud.drop("Class", axis=1)
df2['labels'] = 'real'
df2.columns = df.columns

combined_df = pd.concat([df, df2])
combined_df


df_combined = pd.concat([df2, df])
df_combined

#Compare the distribution of real and synthetic fradulent data points
for col in combined_df.columns:
  plt.figure()
  fig = px.histogram(combined_df, color = 'labels', x=col,barmode="overlay", title = f'Feature {col}', width = 640, height = 500)
  fig.show()