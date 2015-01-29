################################################################################
#from https://groups.google.com/forum/#!topic/pywavelets/xk3UeFz9ZK0
# 
################################################################################

import pywt,pdb 
from numpy import * 

def iswt(coefficients, wavelet): 
  """ 
  Input parameters: 

    coefficients 
      approx and detail coefficients, arranged in level value 
      exactly as output from swt: 
      e.g. [(cA1, cD1), (cA2, cD2), ..., (cAn, cDn)] 

    wavelet 
      Either the name of a wavelet or a Wavelet object 

  """ 
  output = coefficients[0][0].copy() # Avoid modification of input data 

  #num_levels, equivalent to the decomposition level, n 
  num_levels = len(coefficients) 
  #a={}
  for j in range(num_levels,0,-1): 
    step_size = int(pow(2, j-1)) 
    last_index = step_size 
    _, cD = coefficients[num_levels - j] 
    # pdb.set_trace()
    # output is the same for every level
    
    for first in range(last_index): # 0 to last_index - 1 
      # Getting the indices that we will transform 
      indices = arange(first, len(cD), step_size) 
      #print first, indices 

      # select the even indices 
      even_indices = indices[0::2] 
      # select the odd indices 
      odd_indices = indices[1::2] 
      
      # perform the inverse dwt on the selected indices, 
      # making sure to use periodic boundary conditions 
      x1 = pywt.idwt(output[even_indices], cD[even_indices], wavelet, 'per') 
      x2 = pywt.idwt(output[odd_indices], cD[odd_indices], wavelet, 'per') 
      # perform a circular shift right 

      # original: 
      #x2 = roll(x2, 1) 
      # average and insert into the correct indices 
      #output[indices] = (x1 + x2)/2. 

      #modified to allow exact reconstruction of original data, if swt2 is used 
      # with start_level = 0, and wavelet is haar or db1 
      output[even_indices] = x1[0::2] 
      output[odd_indices] = x2[0::2] 
    #a[str(j)]=output
    
  #from pylab import *
  #fig = figure()
  #ax = fig.add_subplot(111)
  #ax.plot(a['1'],'-')
  #ax.plot(a['2'],'r--')
  #ax.plot(a['3'],'.')
  #pdb.set_trace()   
  return output 



def iswt2(coefficients, wav): 
  """ 
  Input parameters: 

    coefficients 
      Approx and detail coefficients, arranged in level value 
      exactly as output from swt2: 
      e.g. [(cA_n, (cH_n, cV_n, cD_n)), (cA_n+1, (cH_n+1, cV_n+1, cD_n +1)), ...] 

      Note: for accurate reconstruction of original data, swt2 must be used with 
      start_level = 0, unless wavelet is haar or db1 (see modification of iswt). 

    wavelet 
      The name of a wavelet 

  """ 

  Level = len(coefficients) 
  Range = range(Level) 
  Range.reverse() 
  Shape = coefficients[0][1][0].shape 

  Out = zeros(Shape,'d') 
  for iRange in Range: 
    C1 = coefficients[iRange] 

    approx = C1[0] 
    LL = transpose(approx) 
    LH = transpose(C1[1][0]) 
    HL = transpose(C1[1][1]) 
    HH = transpose(C1[1][2]) 

    H = zeros(Shape,'d') 
    L = zeros(Shape,'d') 

    for i in range(H.shape[0]): 
      coef = [(HL[i], HH[i])] 
      out = iswt(coef, wav) 
      H[i] = out 

    H = H.T 

    for i in range(L.shape[0]): 
      coef = [(LL[i], LH[i])] 
      out = iswt(coef, wav) 
      L[i] = out 
    L = L.T 

    for i in range(Out.shape[0]): 
      coef = [(L[i], H[i])] 
      out = iswt(coef, wav) 
      Out[i] = out 

  return Out 