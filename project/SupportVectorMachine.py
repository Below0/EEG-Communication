import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn import datasets
from sklearn.svm import LinearSVC
#from mlxtend.plotting import category_scatter
from sklearn.model_selection import train_test_split, GridSearchCV

class SupportVectorMachine:

    def __init__(self):
        self._red_RGB = (1,0,0)
        self._blue_RGB = (0,0,1)
        self._data_colors = [self._red_RGB,self._blue_RGB]

    def _readPointsFromFile(self,filename):
        points = []
        with open(filename, "r") as f:
            for point in f:
                point = point.strip("\n").split(",")
                if(not point[0] is ''):
                    x = int(point[6]) # low beta
                    y = int(point[7]) # high beta
                    xy = [x,y]
                    points.append(xy)
        return points

    def _readDataFromFile(self,class_0_file,class_1_file):
        points_label0 = self._readPointsFromFile(class_0_file) # read data from file1
        points_label1 = self._readPointsFromFile(class_1_file) # read data from file2
        points = points_label0 + points_label1
        points = np.array(points)

        label0, label1 = [0],[1]

        # points_label0 : current measurements
        # points_label1 : emergency measurements
        num_of_label0, num_of_label1 = len(points_label0), len(points_label1)

        labels = label0 * num_of_label0 + label1 * num_of_label1

        return (points,labels)

    def _plotData(self,X_train, y_train, X_test, y_test):

        X = np.concatenate((X_train, X_test))
        y = np.concatenate((y_train, y_test))

        colors = self._getColors(y)
        colors_train = self._getColors(y_train)
        colors_test = self._getColors(y_test)

        plt.figure(figsize=(12, 4), dpi=150)
        # Plot all data plot
        plt.subplot(131) # grid 1
        plt.axis('equal') # equal : 비율 맞춰줌
        plt.scatter(X[:, 0], X[:, 1],c=colors,s=10,edgecolors=colors)
        plt.title("Data (100%)")

        # training data plot
        plt.subplot(132) # grid 2
        plt.axis('equal')
        #plt.axis('off')
        plt.scatter(X_train[:, 0], X_train[:, 1], c = colors_train, s = 10, edgecolors=colors_train)
        plt.title("Training Data (80%)")

        # testing data plot
        plt.subplot(133) # grid 3
        plt.axis('equal')
        #plt.axis('off')
        plt.scatter(X_test[:, 0], X_test[:, 1], c = colors_test, s = 10, edgecolors=colors_test)
        plt.title("Test Data (20%)")
        plt.tight_layout()
        plt.show()

    def _getColors(self,y):
        return [self._data_colors[label] for label in y]

    def _trainRegularization(self,trainValue,testValue):
        trainValue = np.array(trainValue)
        trainValue_min = trainValue.min(axis=0)
        trainValue_max = trainValue.max(axis=0)

        trainValue_range = trainValue_max - trainValue_min
        trainValue_scaled = (trainValue-trainValue_min) / trainValue_range
        testValue_scaled = (testValue-trainValue_min)/trainValue_range

        trainValue_scaled = trainValue_scaled.tolist()
        testValue_scaled = testValue_scaled.tolist()

        return trainValue_scaled,testValue_scaled

    def _plotDecisionFunction(self,X_train, y_train, X_test, y_test, clf):
        plt.figure(figsize=(8, 4), dpi=150)
        plt.subplot(121)
        plt.title("Training data")
        self._plotDecisionFunctionHelper(X_train, y_train, clf)
        plt.subplot(122)
        plt.title("Test data")
        self._plotDecisionFunctionHelper(X_test, y_test, clf, True)
        plt.show()

    def _plotDecisionFunctionHelper(self,X, y, clf, show_only_decision_function = False):

        colors = self._getColors(y)
        plt.axis('equal')
        plt.tight_layout()
        #plt.axis('off')

        plt.scatter(X[:, 0], X[:, 1], c=colors, s=10, edgecolors=colors)
        ax = plt.gca()
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Create grid to evaluate model
        xx = np.linspace(xlim[0], xlim[1], 30)
        yy = np.linspace(ylim[0], ylim[1], 30)
        YY, XX = np.meshgrid(yy, xx)
        xy = np.vstack([XX.ravel(), YY.ravel()]).T # xy.shape = (900, 2)
        Z = clf.decision_function(xy).reshape(XX.shape)
        # clf.decision_function(xy).shape = (900,)
        # Z.shape = (30, 30)

        if(show_only_decision_function):
        # Plot decision boundary
            ax.contour(XX, YY, Z, colors='k', levels=[0], alpha=0.5,linestyles=['-'])
        else:
        # Plot decision boundary and margins
            ax.contour(XX, YY, Z, colors='k', levels=[-1, 0, 1], alpha=0.5,linestyles=['--', '-', '--'])
        # Plot support vectors
        # ax.scatter(clf.support_vectors_[:, 0], clf.support_vectors_[:, 1], s = 10,
        # linewidth=1, facecolors='k', c = 'k', label='Support Vectors')
        # plt.legend(fontsize='small')
