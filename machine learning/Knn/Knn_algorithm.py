# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 11:36:17 2018

@author: outao
"""
from sklearn import neighbors
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family']='SimHei'#设置字体为黑体
matplotlib.rcParams['font.size']=15
os.chdir(r'C:\Users\outao\Desktop\test')
data=pd.read_csv('Knn-movie.csv').values
x_train=data[:,1:3]
y_train=data[:,3].tolist()
knn=neighbors.KNeighborsClassifier(n_neighbors=5)
knn.fit(x_train,y_train)
print ('------------------预测结果----------------------')
print (knn.predict([[18,90]]))
ax=plt.subplot(111)
ax.set_xlabel('武打镜头')
ax.set_ylabel('接吻镜头')
for each in x_train.tolist():
    plt.plot(each[0],each[1],marker='o',color='blue')
plt.plot(18,90,'o',color='red',label='test_sample')
plt.savefig('test.jpg')
plt.show()

    
    
    