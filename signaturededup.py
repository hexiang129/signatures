from tqdm import tqdm
import numpy as np
import pandas as pd

threshold = 11 #from last row in excel template
validratio = 0.70  #assume 75% of it is valid, must change together with threshold

totalSigCnt=int(21.3268*10000)  #assume we submit 195k signatures

dupratioAmongValid = 0.03 #assume among the valid signatures, 2% are duplicate
sampleRate = 0.03 
trialCnt = 5000
print('validRatio={0:4.3f}, duplicateAmongValid={1:4.3f}, sampleRatio={2:4.3f}\n'.format(validratio, dupratioAmongValid, sampleRate))

totalvalidCnt = int(totalSigCnt * validratio)

duplicateCnt = int(totalvalidCnt * dupratioAmongValid) #and 1% of valid signatures are duplicate
print('expect duplicate signatures {0}'.format(duplicateCnt))
distinctCnt = (totalvalidCnt - 2 * duplicateCnt) + duplicateCnt

invalidCnt = totalSigCnt -totalvalidCnt


sigSpace = list(range(distinctCnt))
sigSpace.extend(list(range(duplicateCnt)))
sigSpace.extend(list([-1]*invalidCnt))


sampleCnt = int(totalSigCnt * sampleRate)
print('there are total {0} signatures, {1} unique signatures, sample {2} signatures\n'.format(len(sigSpace), len(np.unique(sigSpace)), sampleCnt))

duplicateCnts = []
for i in tqdm(range(trialCnt)):
    sampledSig = np.random.choice(sigSpace, sampleCnt, replace=False)
    validSampleSig = [x for x in list(sampledSig) if x >=0]
    uniqueSampleSig = np.unique(validSampleSig)
    duplicateCnt = len(validSampleSig)-len(uniqueSampleSig)
    duplicateCnts.append(duplicateCnt)


df=pd.DataFrame({"cnt":duplicateCnts})
df.to_csv('cnt.csv', index=None)
print(df['cnt'].describe())
print(df['cnt'].quantile(0.9))
failedratio = df[df['cnt']>=threshold].shape[0]/df.shape[0]
print('failed ratio={0:5.4f}, {1} out of {2} times, threshold={3}'.format(failedratio,  df[df['cnt']>=threshold].shape[0], df.shape[0], threshold))


