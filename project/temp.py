from sklearn.svm import SVC

svm = SVC(kernel='linear',C=1.0, random_state=0)
# 로지스틱 회귀에서의 C와 반대의 개념. 모델을 조율해주는 값이라고 보면 됨.
svm.fit(X_train_std, y_train)
y_pred_svc = svm.predict(X_test_std)
print('Accuracy: %.2f' % accuracy_score(y_test, y_pred_svc))

import matplotlib.pyplot as plt
import numpy as np

np.random.seed(0)
X_xor = np.random.randn(200, 2)
y_xor = np.logical_xor(X_xor[:, 0] > 0,
                       X_xor[:, 1] > 0)
y_xor = np.where(y_xor, 1, -1)

plt.scatter(X_xor[y_xor == 1, 0],
            X_xor[y_xor == 1, 1],
            c='b', marker='x',
            label='1')
plt.scatter(X_xor[y_xor == -1, 0],
            X_xor[y_xor == -1, 1],
            c='r',
            marker='s',
            label='-1')

plt.xlim([-3, 3])
plt.ylim([-3, 3])
plt.legend(loc='best')
plt.tight_layout()
# plt.savefig('./figures/xor.png', dpi=300)
plt.show()

svm = SVC(kernel='rbf', C=10.0, random_state=0, gamma=0.10)
svm.fit(X_xor, y_xor)
y_pred_ksvc = svm.predict(X_xor)
print('Accuracy: %.2f' % accuracy_score(y_xor, y_pred_ksvc))
