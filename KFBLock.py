import numpy as np
import scipy.integrate as integral
class KFBlock():
    def __init__(self):
        self.prParam = None

    def setR(self, guess, sign):
        self.R = np.ones((3,3), dtype=np.float32)
        self.R[0, 0] *= 10 ** guess[0, 0]
        self.R[1, 1] *= 10 ** guess[0, 1]
        self.R[2, 2] *= 10 ** guess[0, 2]
        self.R[1, 0] *= sign[0, 0]  * 10 ** guess[0, 3]
        self.R[2, 0] *= sign[0, 1]  * 10 ** guess[0, 4]
        self.R[2, 1] *= sign[0, 2]  * 10 ** guess[0, 5]
        self.R[0, 1] = self.R[1, 0]
        self.R[0, 2] = self.R[2, 0]
        self.R[1, 2] = self.R[2, 1]
        np.set_printoptions(precision=16)
        print(self.R)

    def runKF(self, dt, prSig, mSig, mCov):
        N = prSig.shape[0]
        result = np.zeros((N,3))
        sysCov = np.zeros((N,3,3))
        for i in range(1, N):
            # prediction
            prX = result[i-1,:] + prSig[i]*dt[i]
            prCov = sysCov[i-1,:] + self.R

            # K gain
            K = np.linalg.inv(prCov + mCov[i])
            K = np.matmul(prCov, K)
            innov = mSig[i] - prX

            # correction
            corrX = prX + np.matmul(K, innov)
            corrCov = prCov - np.matmul(K, prCov)

            result[i] = corrX
            sysCov[i] = corrCov

        return result, sysCov


def standardize(data):
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    z = (data - mean)/std
    return z

def ClacSTDRMSE(data, gt):
    stdData = standardize(data)
    stdGT = standardize(gt)
    return CalcRMSE(stdData, stdGT)


def integrate(data):
    return integral.cumtrapz(data, axis=0)

def CalcRMSE(data, gt):
    velRMSE = RMSE(data, gt)
    intData = integrate(data)
    intGT = integrate(gt)
    posRMSE = RMSE(intData, intGT)
    return velRMSE, posRMSE

def RMSE(data, gt):
    err = data - gt
    se = err**2
    mse = np.mean(se, axis=0)
    rmse = np.sqrt(mse)
    return rmse

class RewardManager():
    def __init__(self):
        self.RMax = np.array([-9, -9, -9], dtype=np.float32)
        self.minRMSE = np.array([999, 999, 999], dtype=np.float32)

    def GetReward(self, val):
        R = np.array([0,0,0], dtype=np.float32)
        for i in range(0, 3):
            if val[i] <= self.minRMSE[i]:
                R[i] = np.random.normal(self.minRMSE[i], val[i])
                self.minRMSE[i] = val[i]


        return R