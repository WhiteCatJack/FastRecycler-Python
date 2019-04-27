# -*- coding: utf-8 -*-

# 差分处理
def difference(dataset, interval=1):
    diff = list()
    for i in range(interval, len(dataset)):
        value = dataset[i] - dataset[i - interval]
        diff.append(value)
    return diff


# 逆差分处理
def difference_inv(data_diff, dtafir, interval=1):
    diff_inv = dtafir
    for i in range(len(data_diff)):
        value = diff_inv[i] + data_diff[i]
        diff_inv.append(value)
    return diff_inv


# 自协方差函数(k值默认为15),dta的下标是从0~原始数据长度-差分阶数-1(30个数据一阶差分时：0~28)
def self_covariance(dta, k):
    for kk in range(k + 1):
        sum = 0
        for j in range(dta_len - kk):
            # print j,j+kk
            sum = sum + dta[j] * dta[j + kk]
        gamma.append(1 / float(len(dta)) * sum)
        # print 'gamma:',gamma
    return gamma


# 样本自相关函数
def autocorrelation(gamma):
    rou = [i / gamma[0] for i in gamma]
    return rou


# 样本偏相关函数
def partial_correlation(rou, k):
    fai_ex = [1]
    fai = [[0] * (k + 1) for i in range(k + 1)]  # 初始化整个数组
    fai[0][0] = 1
    fai[1][1] = rou[1]  # k=1时，fai[1][1]=rou[1]
    fai_ex.extend([fai[1][1]])
    for kk in range(1, k):  # 当kk=1,2,3....k
        # 计算fai[k+1][k+1]
        sum_up = 0
        sum_down = 0
        for j in range(1, kk + 1):  # j=1,2,...k
            sum_up = sum_up + rou[kk + 1 - j] * fai[kk][j]
            sum_down = sum_down + rou[j] * fai[kk][j]
        fai[kk + 1][kk + 1] = (rou[kk + 1] - sum_up) / (1 - sum_down)
        fai_ex.extend([fai[kk + 1][kk + 1]])
        for j in range(1, kk + 1):  # j=1,2,...k
            fai[kk + 1][j] = fai[kk][j] - fai[kk + 1][kk + 1] * fai[kk][kk - j + 1]  # 计算fai[k+1][j]
    return fai_ex, fai


# AR(p)模型参数估计
def model_ar(p, fai):
    fai_mao = [0]
    sum_sigma = 0
    # 计算fai的参数值
    for j in range(1, p + 1):
        fai_mao.extend([fai[p][j]])
        sum_sigma = sum_sigma + fai_mao[j] * gamma[j]
    # 计算白噪声方差
    sigma2_AR = gamma[0] - sum_sigma
    return fai_mao, sigma2_AR


# MA(1)模型参数估计
def model_ma(rou, q=1):
    tt = 1 + pow((1 - 4 * rou[1] * rou[1]), 0.5)
    theta_1 = (-2 * rou[1]) / tt
    sigma2_MA = rou[0] * tt / 2
    return theta_1, sigma2_MA


# ARMA(p,1)参数估计
def model_arma(p, q, fai_mao):
    # fai_mao,sigma2_ar=ar_pre.model_ar(p)
    gammak_w = [0, 0]
    # 得到gamma_0_w
    sum_L = 0
    sum_last = 0
    for L in range(1, p + 1):
        sum_j = 0
        for j in range(1, p + 1):
            sum_j = sum_j + fai_mao[L] * fai_mao[j] * gamma[abs(L - j)]
        sum_L = sum_L + sum_j
    for j in range(1, p + 1):
        sum_last = sum_last + fai_mao[j] * gamma[abs(-j)] + fai_mao[j] * gamma[j]
    gammak_w[0] = gamma[0] + sum_L - sum_last
    # 得到gamma_1_w
    sum_L = 0
    sum_last = 0
    for L in range(1, p + 1):
        sum_j = 0
        for j in range(1, p + 1):
            sum_j = sum_j + fai_mao[L] * fai_mao[j] * gamma[abs(L - j + 1)]
        sum_L = sum_L + sum_j
    for j in range(1, p + 1):
        sum_last = sum_last + fai_mao[j] * gamma[abs(1 - j)] + fai_mao[j] * gamma[1 + j]
    gammak_w[1] = gamma[1] + sum_L - sum_last
    rouk_w = gammak_w[1] / gammak_w[0]
    theta1_ARMA = (-2 * rouk_w) / (1 + pow(1 - 4 * rouk_w * rouk_w, 0.5))
    return theta1_ARMA


##########################################################################
# (dta,L,k)
def func(dta, L, k):
    global dta_len, gamma, diff_n
    diff_n = 1
    gamma = []
    # 计算差分运算
    dta_diff = difference(dta, diff_n)
    dta_len = len(dta_diff)  # 数据长度
    mean_dta = 1 / float(dta_len) * sum(dta_diff)  # 求均值
    dta_w = [i - mean_dta for i in dta_diff]  # 样本变成W_t
    # 计算自协方差
    gamma = self_covariance(dta_w, k)
    # print 'gamma:',gamma
    # 计算自相关函数
    rou = autocorrelation(gamma)
    # print 'rou:',rou
    # 计算偏相关函数
    fai_ex, fai = partial_correlation(rou, k)
    # print 'fai_ex,fai:',fai_ex,fai
    # print('(fai_ex,fai) is ok!!')
    return dta_diff, dta_len, gamma, mean_dta, dta_w, rou, fai_ex, fai
