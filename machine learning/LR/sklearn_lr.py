# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 16:04:44 2018

@author: outao
"""
#使用sklearn库实现LR分类
#-------------------------------------------------------------
import numpy as np
import os
import pandas as pd
from sklearn.linear_model import LogisticRegression 
import matplotlib.pyplot as plt
os.chdir(r'C:\Users\outao\Desktop\机器学习\机器学习数据集\Datasets\Breast-Cancer')
train_data=pd.read_csv('breast-cancer-train.csv').values
X_train=train_data[:,1:3]
y_train=train_data[:,3]
lr=LogisticRegression()
#print (X_train)
#print (type(y_train))
lr.fit(X_train,y_train)#=训练过程不可见
#获取测试样本
test_data=pd.read_csv('breast-cancer-test.csv').values
test_input=test_data[:,1:3]
result=lr.predict(test_input).tolist()
#------------------------------------------------------------


#画出测试集样本点
ax=plt.subplot(111)
ax.set_xlabel('Clump Thickness')
ax.set_ylabel('Cell Size')
plt_data=train_data[:,1:4]
for each in plt_data.tolist():
    if each[2]==0:
        plt.plot(each[0],each[1],'ro')
    else:
        plt.plot(each[0],each[1],'kx')
plt.savefig('breast-cancer.jpg')
plt.show()
count=0
for each in plt_data.tolist():
    if each[2]==0:
        count+=1
print (count)
        
