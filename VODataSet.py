from torch.utils.data import Dataset, DataLoader
from PrepData import DataManager
import numpy as np
import cv2
import time
from sklearn.utils import shuffle

class VODataSetManager_RCNN():
    def __init__(self, dsName='airsim', subType='mr', seq=[0], isTrain=True, split=0.2):
        data = DataManager()
        data.initHelper(dsName, subType, seq)
        data.standardizeImgs(isTrain)

        delay = 10
        N = data.numTotalData
        possibleN = N - delay
        idx = np.arange(0, possibleN, 1)

        if isTrain:
            idx = shuffle(idx)
            valN = int(possibleN * split)
            trainN = possibleN - valN
            trainIdx = idx[0:trainN]
            valIdx = idx[trainN:]
            self.trainSet = VODataSet_RCNN(trainN, trainIdx)
            self.valSet = VODataSet_RCNN(valN, valIdx)
        else:
            self.testSet = VODataSet_RCNN(possibleN, idx)

class VODataSet_RCNN(Dataset):
    def __init__(self, N, idxList):
        self.dm = DataManager()
        self.N = N
        self.idxList = idxList
        self.delay = 10

    def __getitem__(self, i):
        index = self.idxList[i]
        try:
            return self.dm.imgs[index:index+self.delay], self.dm.imgs[index+1:index+1+self.delay],\
                   self.dm.du[index:index+self.delay], self.dm.dw[index:index+self.delay], \
                   self.dm.dtr[index:index+self.delay]
        except:
            print('this is an error @ VODataSet_CNN of VODataSet.py')
            print(self.dm.imgs.shape)
            print(i, index)

    def __len__(self):
        return self.N


if __name__ == '__main__':
    start = time.time()
    dm = VODataSetManager_RCNN(dsName='airsim', subType='mr', seq=[2], isTrain=False)
    print(time.time() - start)
    #trainSet, valSet = dm.trainSet, dm.valSet
    dataSet = dm.testSet
    trainLoader = DataLoader(dataset = dataSet, batch_size=64)
    sum = 0
    for batch_idx, (img0, img1, du, dw, dtrans) in enumerate(trainLoader):
        img0 = img0.data.numpy()
        img1 = img1.data.numpy()
        sum += img0.shape[0]

        for i in range (img0.shape[0]):
            img_t0 = img0[i,:]
            img_t1 = img1[i,:]
            img_t0 = np.reshape(img_t0, (360, 720, 3))
            img_t1 = np.reshape(img_t1, (360, 720, 3))
            imgcon = img_t1 - img_t0
            cv2.imshow('img0', img_t0)
            cv2.imshow('img1', img_t1)
            cv2.imshow('imgcon', imgcon)
            cv2.waitKey(1)



