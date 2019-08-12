from tqdm import tqdm
import numpy as np
import pandas as pd

def getthreshold(totalSigCnt, samplerate, SigCntNeeded, sampleValidRatio):
    sampleCnt = totalSigCnt * samplerate
    totalInvalidSigCntExpect = totalSigCnt * (1-sampleValidRatio)
    totalInvalidSigCntUb = totalInvalidSigCntExpect + 1.5 * (totalInvalidSigCntExpect**0.5)
    maxAllowedDupInTotal = totalSigCnt - SigCntNeeded - totalInvalidSigCntUb
    maxAllowedDupInSample = maxAllowedDupInTotal * samplerate * samplerate
    maxAllowedDupInSampleUb = maxAllowedDupInSample - 1.6 * (maxAllowedDupInSample **0.5)
    return maxAllowedDupInSampleUb
    
threshold = 11 #from last row in excel template
validratio = 0.72  #assume 75% of it is valid, must change together with threshold

totalSigCnt=int(21.3268*10000)  #assume we submit 195k signatures
neededSigCnt = int(13*10000)
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
thresholds = []
for i in tqdm(range(trialCnt)):
    sampledSig = np.random.choice(sigSpace, sampleCnt, replace=False)
    validSampleSig = [x for x in list(sampledSig) if x >=0]
    sampleValidRatio = len(validSampleSig) / len (sampledSig)
    threshold = getthreshold(totalSigCnt, sampleRate, neededSigCnt, sampleValidRatio)
    thresholds.append(threshold)
    uniqueSampleSig = np.unique(validSampleSig)
    duplicateCnt = len(validSampleSig)-len(uniqueSampleSig)
    duplicateCnts.append(duplicateCnt)
    



df=pd.DataFrame({"cnt":duplicateCnts, "threshold":thresholds})
df.to_csv('cnt.csv', index=None)
print(df['cnt'].describe())
print(df['cnt'].quantile(0.9))
failedratio = df[df['cnt']>=df['threshold']].shape[0]/df.shape[0]
print('failed ratio={0:5.4f}, {1} out of {2} times, average threshold={3:5.3f}, min/max threshold={4:5.3f},{5:5.3f}, 1% percentile threshold={6:5.3f}'.format(failedratio,  df[df['cnt']>=threshold].shape[0], df.shape[0], df['threshold'].mean(), df['threshold'].min(), df['threshold'].max(), df['threshold'].quantile(0.1)))


