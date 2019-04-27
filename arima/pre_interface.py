# -*- coding: utf-8 -*-
import arima.functions_related  as fr


# AR(P)模型预测未来7天的数量和(dta,p,L,k)
def ar_pre(dta, p, L, k):
    # 得到AR模型
    fai_mao, sigma2_ar = fr.model_ar(p, fai)
    len_pre = dta_len - 1
    dta_pre = dta_diff[:]  # dta_pre的改变不会影响fr.dta_diff原数据
    fai_sum = 0
    for i in range(1, p + 1):
        fai_sum = fai_sum + fai_mao[i]
    theta0_ARpre = mean_dta * (1 - fai_sum)
    for LL in range(1, L + 1):
        z_k = 0
        for pp in range(1, p + 1):
            z_k = z_k + fai_mao[pp] * dta_pre[len_pre + LL - pp]  # 数据是从后往前的
        dta_pre.extend([theta0_ARpre + z_k])
    # 逆差分处理(差分数据,原数据的前n阶个,差分阶数)
    AR_pre_inv = fr.difference_inv(dta_pre, dta[0:fr.diff_n], fr.diff_n)
    return AR_pre_inv[dta_len + 1:], sum(AR_pre_inv[dta_len + 1:]), AR_pre_inv


# ARMA(P,1)模型预测未来7天的数量和(dta,p,q,L,k)
def arma_pre(dta, p, q, L, k):
    # global fai_mao,sigma2_ar
    fai_mao, sigma2_ar = fr.model_ar(p, fai)
    # 得到ARMA(P,1)模型
    theta1_ARMA = fr.model_arma(p, q, fai_mao)
    z = dta_diff[:]
    len_z = dta_len - 1
    alpha = [0]
    mea = mean_dta
    # 计算theta0初始值
    fai_sum = 0
    for i in range(1, p + 1):
        fai_sum = fai_sum + fai_mao[i]
    theta0_ARMApre = mean_dta * (1 - fai_sum)
    # 计算alpha_k
    for k in range(1, dta_len):
        sum_fai = 0
        for pp in range(1, p + 1):
            if k - pp - 1 < 0:
                sum_fai = sum_fai + fai_mao[pp] * mea
            else:
                sum_fai = sum_fai + fai_mao[pp] * z[k - pp - 1]
        alpha_tt = -theta0_ARMApre + z[k - 1] - sum_fai + theta1_ARMA * alpha[k - 1]
        alpha.extend([alpha_tt])
    sum_k1 = 0
    for pp in range(1, p + 1):
        sum_k1 = sum_k1 + fai_mao[pp] * z[len_z + 1 - pp]
    z_k1 = theta0_ARMApre + sum_k1 - theta1_ARMA * alpha[-1]
    z.extend([z_k1])
    for LL in range(2, L + 1):
        sum_pp = 0
        for pp in range(1, pp + 1):
            sum_pp = sum_pp + fai_mao[pp] * z[len_z + LL - pp]
        z.extend([theta0_ARMApre + sum_pp])
    # 逆差分处理(差分数据,原数据的前n阶个,差分阶数)
    ARMA_pre_inv = fr.difference_inv(z, dta[0:fr.diff_n], fr.diff_n)
    return ARMA_pre_inv[dta_len + 1:], sum(ARMA_pre_inv[dta_len + 1:]), ARMA_pre_inv


# MA(1)模型预测预测未来7天的数量和(dta,q,L,k)
def ma_pre(dta, q, L, k):
    # 得到MA(1)模型
    theta_1, sigma2_ma = fr.model_ma(rou, 1)
    z = dta_diff[:]
    tt = dta_diff[0] - mean_dta
    alpha = [0, tt]
    for t in range(2, fr.dta_len):
        mm = dta_diff[t - 1] - mean_dta + theta_1 * alpha[t - 1]
        alpha.extend([mm])
    z.extend([mean_dta - theta_1 * alpha[-1]])
    z.extend([mean_dta] * (L - 1))
    # 逆差分处理(差分数据,原数据的前n阶个,差分阶数)
    MA_pre_inv = fr.difference_inv(z, dta[0:fr.diff_n], fr.diff_n)
    return MA_pre_inv[dta_len + 1:], sum(MA_pre_inv[dta_len + 1:]), MA_pre_inv


# 预测接口
def interface_pre(dta, model, p, q=1, L=7, k=20):
    global dta_diff, dta_len, gamma, mean_dta, dta_w, rou, fai_ex, fai, AR_pre_inv
    dta_diff, dta_len, gamma, mean_dta, dta_w, rou, fai_ex, fai = fr.func(dta, L, k)
    if model == 1:
        AR_pre7, AR_sum7, AR_pre_inv = ar_pre(dta, p, L, k)
        return AR_pre7, AR_sum7, AR_pre_inv
    elif model == 2:
        MA_pre7, MA_sum7, MA_pre_inv = ma_pre(dta, q, L, k)
        return MA_pre7, MA_sum7, MA_pre_inv
    else:
        ARMA_pre7, ARMA_sum7, ARMA_pre_inv = arma_pre(dta, p, q, L, k)
        return ARMA_pre7, ARMA_sum7, ARMA_pre_inv


def predict(dta, day_after):
    ARIMA_pre_list, ARIMA_pre_list_sum, ARIMA_pre_inv = interface_pre(dta, model=3, p=2, q=2, L=day_after, k=20)
    return ARIMA_pre_list
