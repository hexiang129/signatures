'''
this file implements the sampled signature verification algorithm used by WA state
and simulate how likely a referendum will pass the verification under given valid signature ratio and duplicate signature ratio
'''
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
    
validratio = 0.72  #assume 72% of submitted signatures are valid
totalSigCnt=int(21.3268*10000)  #total number of signatures we submitted
neededSigCnt = int(13*10000)    #how many signatures are neeeded to qualify the referendum
dupratioAmongValid = 0.03 #assume among the valid signatures, 3% are duplicate
sampleRate = 0.03   #sample rate used by WA secretary of state. should always be 3%
trialCnt = 5000     #number of monte carlo trials
print('validRatio={0:4.3f}, duplicateAmongValid={1:4.3f}, sampleRatio={2:4.3f}\n'.format(validratio, dupratioAmongValid, sampleRate))

totalvalidCnt = int(totalSigCnt * validratio)

duplicateCnt = int(totalvalidCnt * dupratioAmongValid) 
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


