# -*- coding: utf-8 -*-
import time
import pickle
import numpy as np
import pandas as pd
from datetime import datetime as dt
        

class TradingRRL(object):
    def __init__(self, T=1000, M=10, init_t=10000, mu=10000, sigma=0.02, rho=1.0, n_epoch=1 , period=2000 , TT=1, q_threshold = 0.7, ini_A = 10, ini_B = 1000, eta = 0.01, amp = 1, experimentnumber = 1):
        self.period = period
        self.TT = TT
        self.T = T
        self.M = M
        self.init_t = init_t
        self.mu = mu
        self.sigma = sigma
        self.rho = rho
        self.all_t = None
        self.all_p = None
        self.all_preward = None
        self.t = None
        self.p = None
        self.preward =  None
        self.r = None
        self.rnorm = np.empty(0)
        self.rreward = None
        self.x = np.zeros([TT, M+2])
        self.F = np.zeros(1)
        self.R = np.zeros(TT)
        # self.w = np.ones(M+2)
        # np.random.seed(123)
        self.amp = amp
        self.iniw = np.sort(self.amp*np.random.normal(4,1,(M+2)))[::-1]
        # self.iniw[0] = 1
        self.iniw[-1] = 0
        self.w = self.iniw 
        self.ww = np.empty(0)
        # self.w_opt = np.ones(M+2)
        self.S_opt = -1000
        self.ini_A = ini_A
        self.ini_B = ini_B
        self.A = ini_A
        self.B = ini_B
        self.Bstorage = np.empty(0)
        self.Astorage = np.empty(0)
        self.ASR = ini_A
        self.BSR = ini_B
        self.numofPS = np.zeros(1)
        self.numofNS = np.zeros(1)
        self.numofPA = np.zeros(1)
        self.numofNA = np.zeros(1)
        self.epoch_S = np.empty(0)
        self.epoch_SR = np.empty(0)
        self.FF = np.zeros(1)
        self.FFF = np.zeros(1)
        self.pp = np.empty(0)
        self.sumRR = np.zeros(0)
        self.n_epoch = n_epoch
        self.progress_period = 100
        self.q_threshold = q_threshold
        self.eta = eta
        self.experimentnumber = experimentnumber
        self.storageweights = self.w
        self.storagedSdweights = np.zeros(M+2)
        self.storage_bias = np.empty(0)
        self.storage_mr = np.empty(0)
        self.storage_wf = np.empty(0)

    def load_csv(self, fname): # 1:2 column to self.all_t 650002 , the 6th column pure in the all_P
        tmp = pd.read_csv(fname, header=None)
        # tmp_tstr = tmp[0] +" " + tmp[1]
        # tmp_t = [dt.strptime(tmp_tstr[i], '%Y.%m.%d %H:%M') for i in range(len(tmp_tstr))]
        tmp_preward = list(tmp[4])
        tmp_p = list(tmp[4])
        # self.all_t = np.array(tmp_t[::-1])
        self.all_p = np.array(tmp_p[::-1])
        self.all_preward = np.array(tmp_preward[::-1])

    def quant(self):
        # self.F[np.where(np.abs(self.F) < self.q_threshold)] = 0
        # self.FQ = self.F
        # self.FQ[np.where(np.abs(self.FQ) < self.q_threshold)] = 0
        # self.FQ = np.sign(self.FQ)
        # self.FFF=self.FF
        self.FF[np.where(np.abs(self.FF) < self.q_threshold)] = 0
        self.FF = np.sign(self.FF)

    def set_t_p_r(self, history): # set t p(z) r from sample init_t to  T+M+1 
        # self.t = self.all_t[self.init_t:self.init_t+self.TT+self.M+1]
        self.p = history[-self.M-1:]
        self.pp = np.append(self.pp, self.p)
        self.preward = history[-self.M-1:]
        self.r = np.diff(self.p)
        self.rreward = np.diff(self.preward)

    def set_x_F(self): # construct decision function (equation 1 in Moody 2001)  
        for i in range(self.TT-1, -1 ,-1):
            self.x[i] = np.zeros(self.M+2)
            self.x[i][0] = 1.0 # for bias
            self.x[i][self.M+2-1] = self.FF[-1] # for last action
            for j in range(1, self.M+2-1, 1):
                self.x[i][j] = self.r[i+j-1] # for r from t to the t-M
            # self.x[i][1:self.M] = self.x[i][1:self.M]/self.sigma
            self.rnorm = np.append(self.rnorm , np.linalg.norm(self.x[i][1:self.M]))
            self.x[i][1:self.M] = self.x[i][1:self.M]/np.linalg.norm(self.x[i][1:self.M])
            self.storage_wf = np.append(self.storage_wf , self.x[i][self.M+2-1]* self.w[0])
            self.storage_mr = np.append(self.storage_mr, np.dot(self.w[1:-1], self.x[i][1:self.M+1]))
            self.storage_bias = np.append(self.storage_bias, self.w[-1])
            # self.F = np.tanh(np.clip(self.x[i][self.M+2-1]* self.w[0],-1,1)+np.dot(self.w[1:-1], self.x[i][1:self.M+1])+np.clip(self.w[-1],-1,1)) # generate current action

            self.F = np.tanh(np.dot(self.w, self.x[i])) # generate current action
            self.FF = np.append(self.FF, self.F)
            self.FFF = np.append(self.FFF, self.F)
        # self.quant()
        self.ww = np.append(self.ww,np.linalg.norm(self.w))
        # self.FF = np.append(self.FF, self.F)
        return self.F

    def calc_R(self): # calculate Rt during T period
        if self.TT == 1:
            self.R = self.mu * (self.FF[-1] * self.rreward[:self.TT] - self.sigma * np.abs(self.FF[-1]-self.FF[-2]))
            self.RSR = np.minimum(0,self.mu * (self.FF[-1] * self.rreward[:self.TT] - self.sigma * np.abs(self.FF[-1]-self.FF[-2])))
            if self.R > 0:
                self.numofPS = self.numofPS + 1
            if self.R < 0:
                self.numofNS = self.numofNS + 1
            if np.abs(self.FF[-1]-self.FF[-2]) != 0 and self.R > 0:
                self.numofPA = self.numofPA + 1
            if np.abs(self.FF[-1]-self.FF[-2]) != 0 and self.R < 0:
                self.numofNA = self.numofNA +1
        if self.TT > 1:
            self.R = self.mu * (self.FF[1:] * self.rreward[:self.TT] - self.sigma * np.abs(-np.diff(self.FF)))
            self.RSR = np.minimum(0,self.mu * (self.FF[1:] * self.rreward[:self.TT] - self.sigma * np.abs(-np.diff(self.FF))))
            self.numofPS = [np.sum(1 for number in self.R if number > 0)]
            self.numofNS = [np.sum(1 for number in self.R if number < 0)]
            self.numofPA = [np.sum(1 for number, numbera in zip(np.diff(self.FF),self.R) if number != 0 and numbera > 0)]
            self.numofNA = [np.sum(1 for number, numbera in zip(np.diff(self.FF),self.R) if number != 0 and numbera < 0)]

    def calc_sumR(self): # calculate Rt and Rt^2 
        self.sumR  = np.cumsum(self.R[::-1])[::-1]
        self.sumRSR  = np.cumsum(self.RSR[::-1])[::-1]
        if len(self.sumRR) > 1: 
            self.sumRR = np.append(self.sumRR, self.sumRR[-1] + self.sumR )
        if len(self.sumRR) < 2:
            self.sumRR = np.append(self.sumRR, self.sumR)

        self.sumR2  = np.cumsum((self.R**2)[::-1])[::-1]
        self.sumR2SR  = np.cumsum((self.RSR**2)[::-1])[::-1]

    def calc_dSdw(self): # calculate differential sharpe ratio
        self.set_x_F()
        self.quant()
        self.calc_R()
        self.calc_sumR()
        if len(self.sumR) > 1:
            self.A      =  self.sumR[0] / self.TT  # average of R on the period T
            self.B      =  self.sumR2[0] / self.TT  # squered of R on the period T
            self.ASR      =  self.sumR[0] / self.T
            self.BSR      =  self.sumR2SR[0] / self.T
        if len(self.sumR) == 1:
            self.A = self.A + self.eta*(self.sumR - self.A)
            self.B = self.B + self.eta*(self.sumR**2 - self.B) 
            self.ASR = self.ASR + self.eta*(self.sumR - self.ASR)
            self.BSR = self.BSR + self.eta*(self.sumRSR**2 - self.BSR) 
            self.Astorage = np.append(self.Astorage, self.A)
            self.Bstorage = np.append(self.Bstorage, self.B)
        self.SR= self.ASR / np.sqrt(self.BSR)    
        # self.S      =  self.A / np.sqrt(np.maximum(self.B - self.A**2,0.001*self.B)) # calculate the ST over period T
        self.S      =  self.A / np.sqrt(self.B - self.A**2) # calculate the ST over period T
        self.dSdA   =  self.S * (1 + self.S**2) / self.A # derivative of equation of equation 12 (Moody 2001) with respect to A  equation is ST=A/(B-A^2) 
        self.dSdB   = -self.S**3 / 2 / self.A**2 # derivative of equation of equation 12 (Moody 2001) with respect to B  equation is ST=A/(B-A^2) 
        self.dAdR   =  1.0 / self.TT # extract from equation 15 (Moody 2001)
        self.dBdR   =  2.0 / self.TT * self.R # extract from equation 15 (Moody 2001)
        if self.TT == 1:
            self.dRdF   = -self.mu * self.sigma * (self.FFF[-1]-self.FFF[-2]) # extract5 from equation 6 (Moody 2001)
            self.dRdFp  =  self.mu * self.r[:self.TT] + self.mu * self.sigma * (self.FFF[-1]-self.FFF[-2]) # extract from equation 6 (Moody 2001)
        if self.TT > 1:
            self.dRdF   = -self.mu * self.sigma * (-np.diff(self.FFF)) # extract5 from equation 6 (Moody 2001)
            self.dRdFp  =  self.mu * self.r[:self.TT] + self.mu * self.sigma * (-np.diff(self.FFF)) # extract from equation 6 (Moody 2001)
        self.dFdw   = np.zeros(self.M+2)
        self.dFpdw  = np.zeros(self.M+2)
        self.dSdw   = np.zeros(self.M+2)
        if self.TT == 1:
            for i in range(self.TT-1, -1 ,-1):
                if i != self.TT-1:
                    self.dFpdw = self.dFdw.copy()
                self.dFdw  = (1 - self.F**2) * (self.x[i] + self.w[self.M+2-1] * self.dFpdw) # derivative of equation 1 (Moody 2001) respect to the weights  U'F'(U)
                self.dSdw = (self.dSdA * self.dAdR + self.dSdB * self.dBdR) * (self.dRdF * self.dFdw + self.dRdFp * self.dFpdw) # calculate equation 28 (Moody 2001) 
                self.update_w()
        if self.TT > 1:
            for i in range(self.TT-1, -1 ,-1):
                if i != self.TT-1:
                    self.dFpdw = self.dFdw.copy()
                self.dFdw  = (1 - self.FFF[i]**2) * (self.x[i] + self.w[self.M+2-1] * self.dFpdw) # derivative of equation 1 (Moody 2001) respect to the weights  U'F'(U)
                self.dSdw = (self.dSdA * self.dAdR + self.dSdB * self.dBdR[i]) * (self.dRdF[i] * self.dFdw + self.dRdFp[i] * self.dFpdw) # calculate equation 28 (Moody 2001) 
                self.update_w()

    def update_w(self):
        # print(self.w)

        # self.dSdw = np.clip(self.dSdw,-1, 1)
        # self.dSdw = self.dSdw/np.max(np.abs(self.dSdw))

        self.w[1:] = self.w[1:] + self.rho * self.dSdw[1:]
        self.w[0] = self.w[0] + 0.25*self.rho * self.dSdw[0]
        # self.w = self.w + self.rho * self.dSdw

        # self.w = np.maximum(self.w, 0.1)
        # self.w[1:-1] = np.minimum(self.w[1:-1], 0.1)
        # self.w[1:-1] = np.maximum(self.w[1:-1], 0)
        # self.w[1:-1] = np.clip(self.w[1:-1], 0,1)
        self.w[1] = np.maximum(self.w[1], 0.01)
        self.w[1] = np.minimum(self.w[1], 2)
        self.w[2:-1] = np.clip(self.w[2:-1], 0.01,self.w[1])
        # self.w = np.maximum(self.w, 0.01)
        self.w[0] = np.clip(self.w[0], 0.01, self.w[1])
        self.w[-1] = np.clip(self.w[-1], 0, 0.25*self.w[0])

        # self.w = np.clip(self.w, 0, 1)

        self.storagedSdweights = np.vstack((self.storagedSdweights, self.dSdw))
        self.storageweights = np.vstack((self.storageweights, self.w))


        # print('*')
        # print(self.rho * self.dSdw)
        # print(self.w)
        


    def fit(self):
        
        pre_epoch_times = len(self.epoch_S)

        # self.calc_dSdw()
        # print("Epoch loop start. Initial sharp's ratio is " + str(self.S) + ".")
        # self.S_opt = self.S
        
        tic = time.clock()
        for e_index in range(self.n_epoch):
            self.calc_dSdw()
            # if self.S > self.S_opt:
            #     self.S_opt = self.S
            #     self.w_opt = self.w.copy()
            self.epoch_S = np.append(self.epoch_S, self.S)
            self.epoch_SR = np.append(self.epoch_SR, self.SR)
            # self.update_w()

        # self.w = self.w_opt.copy()
        # self.calc_dSdw()
        # print("Epoch loop end. Optimized sharp's ratio is " + str(self.S_opt) + ".")

    def save_train(self):
        # df = pd.DataFrame(self.iniw, self.w, self.ww, self.epoch_S)
        with pd.ExcelWriter("16_mov_win_train"+"_experimentnumber="+str(self.experimentnumber)+"_period="+str(self.period)+"_TT="+str(self.TT)+"_T="+str(self.T)+"_M="+str(self.M)+"_mu="+str(self.mu)+"_sigma="+str(self.sigma)+"_rho="+str(self.rho)+"_n_epoch="+str(self.n_epoch)+"_q_threshold="+str(self.q_threshold)+"ini_A"+str(self.ini_A)+"ini_B"+str(self.ini_B)+"eta"+str(self.eta)+"_amp="+str(self.amp)+".xlsx") as writer:
            pd.DataFrame(self.iniw).to_excel(writer, sheet_name = 'iniw', index = None)
            pd.DataFrame(self.w).to_excel(writer, sheet_name = 'w', index = None)
            pd.DataFrame(self.ww).to_excel(writer, sheet_name = 'ww', index = None)
            pd.DataFrame(self.storageweights).to_excel(writer, sheet_name = 'w_through_time', index = None)
            pd.DataFrame(self.storagedSdweights).to_excel(writer, sheet_name = 'gradient_of_w_through_time', index = None)
            pd.DataFrame(self.storage_wf).to_excel(writer, sheet_name = 'W_FP through time', index = None)
            pd.DataFrame(self.storage_mr).to_excel(writer, sheet_name = 'M_R through time', index = None)
            pd.DataFrame(self.storage_bias).to_excel(writer, sheet_name = 'bias through time', index = None)
            pd.DataFrame(self.epoch_S).to_excel(writer, sheet_name = 'epoch_S', index = None)
            pd.DataFrame(self.epoch_SR).to_excel(writer, sheet_name = 'epoch_SR', index = None)
            pd.DataFrame(self.numofPS).to_excel(writer, sheet_name = 'number of profity situations in train', index = None)
            pd.DataFrame(self.numofNS).to_excel(writer, sheet_name = 'number of costy situations in train', index = None)
            pd.DataFrame(self.numofNA).to_excel(writer, sheet_name = 'number of costy Actions in train', index = None)
            pd.DataFrame(self.numofPA).to_excel(writer, sheet_name = 'number of profity Actions in train', index = None)
            pd.DataFrame(self.Astorage).to_excel(writer, sheet_name = 'A during training', index = None)
            pd.DataFrame(self.Bstorage).to_excel(writer, sheet_name = 'B during training', index = None)

    def save_test(self):
        # df = pd.DataFrame(self.iniw, self.w, self.ww, self.epoch_S)
        with pd.ExcelWriter("16_moving_window_test"+"_experimentnumber="+str(self.experimentnumber)+"_period="+str(self.period)+"_TT="+str(self.TT)+"_T="+str(self.T)+"_M="+str(self.M)+"_mu="+str(self.mu)+"_sigma="+str(self.sigma)+"_rho="+str(self.rho)+"_n_epoch="+str(self.n_epoch)+"_q_threshold="+str(self.q_threshold)+"ini_A"+str(self.ini_A)+"ini_B"+str(self.ini_B)+"eta"+str(self.eta)+"_amp="+str(self.amp)+".xlsx") as writer:
            # pd.DataFrame(self.iniw).to_excel(writer, sheet_name = 'iniw', index = None)
            pd.DataFrame(self.w).to_excel(writer, sheet_name = 'w', index = None)
            # pd.DataFrame(self.ww).to_excel(writer, sheet_name = 'ww', index = None)
            # pd.DataFrame(self.epoch_S).to_excel(writer, sheet_name = 'epoch_S', index = None)
            # pd.DataFrame(self.epoch_SR).to_excel(writer, sheet_name = 'epoch_SR', index = None)
            pd.DataFrame(self.numofPS).to_excel(writer, sheet_name = 'number of profity situations in test', index = None)
            pd.DataFrame(self.numofNS).to_excel(writer, sheet_name = 'number of costy situations in test', index = None)
            pd.DataFrame(self.numofNA).to_excel(writer, sheet_name = 'number of costy Actions in test', index = None)
            pd.DataFrame(self.numofPA).to_excel(writer, sheet_name = 'number of profity Actions in test', index = None)
        # pd.DataFrame(self.w).to_excel("16_moving_window"+"T="+str(self.T)+"_M="+str(self.M)+"_sigma="+str(self.sigma)+"_rho="+str(self.rho)+".xlsx", sheet_name="Final_W")
        # pd.DataFrame(self.ww).to_excel("16_moving_window"+"T="+str(self.T)+"_M="+str(self.M)+"_sigma="+str(self.sigma)+"_rho="+str(self.rho)+".xlsx", sheet_name="Wnorm", index=False)
        # pd.DataFrame(self.epoch_S).to_excel("16_moving_window"+"T="+str(self.T)+"_M="+str(self.M)+"_sigma="+str(self.sigma)+"_rho="+str(self.rho)+".xlsx", sheet_name="SR", index=False)
        # pd.DataFrame(self.iniw).to_excel("16_moving_window"+"T="+str(self.T)+"_M="+str(self.M)+"_sigma="+str(self.sigma)+"_rho="+str(self.rho)+".xlsx", sheet_name="ini_W", index=False)

    def load_weight(self):
        tmp = pd.read_csv("w.csv", header=None)
        self.w = tmp.T.values[0]

