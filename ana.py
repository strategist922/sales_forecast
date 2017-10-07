import os
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller as ADF
from statsmodels.tsa.arima_model import ARIMA
import statsmodels.api as sm
from statsmodels.graphics.api import qqplot
from statsmodels.stats.diagnostic import acorr_ljungbox

# data prep
fin = 'data/sales_by_item.xlsx'
out_path = 'result/'
if not os.path.exists(out_path):
    os.makedirs(out_path)
fout = 'result/forecast.xlsx'
mout = 'result/model.xlsx'

dt = pd.read_excel(fin).T # T b/c originally date as column and product as row
dt.index = pd.to_datetime(dt.index)
dt_ana = dt.iloc[:-12, :] # use 2014-2016 data for modeling
dt_tst = dt.iloc[-12:-7, :] # use 2017.01-05 data for testing
dt_prd = dt.iloc[-7: -1, :] # predict 2017.06-11 data

######################################################################
# EDA
figout = 'eda_fig/'
if not os.path.exists(figout):
    os.makedirs(figout)

plt.style.use('ggplot')
for column in dt_ana.columns:
    colout = os.path.join(figout, column + '.png')
    dt_ana[column].plot(figsize=(10,8))
    plt.title(column)
    plt.xlabel('Date')
    plt.ylabel('Sales Quantity')
    plt.savefig(colout, dpi=200)
    plt.close()

######################################################################
# Adfuller test to determine order of diff and potentially opt out new products
diff = dict() # store diff info for every product
p_adf = dict() # store p-value for every product corresponding to diff value

for column in dt_ana.columns:
    adf = ADF(dt_ana[column])
    diff[column] = 0
    p_adf[column] = adf[1]
    while adf[1] >= .05:
        try:
            diff[column] = diff[column] + 1
            adf = ADF(dt_ana[column].diff(diff[column]).dropna())
            p_adf[column] = adf[1]
        except:
            diff[column] = -1

# check the relationship for screening invalid products
[(x, diff[x], p_adf[x]) for x in dt.columns] # command line
# new products have too short records and will be submitted for human decision
new_prod = [k for (k, v) in p_adf.items() if np.isnan(v) or v == 0.0]
# current products are submitted for modeling
cur_prod = [x for x in dt.columns if x not in new_prod]

######################################################################
# plot ACF and PACF
acf_pacf_out = 'acf_pacf_fig/'
if not os.path.exists(acf_pacf_out):
    os.makedirs(acf_pacf_out)

def plot_acf_pacf(data, savefig=False, savename=''):
    lag = len(data) - 1
    fig = plt.figure(figsize=(10,8))
    ax1 = fig.add_subplot(211)
    fig = sm.graphics.tsa.plot_acf(data,lags=lag, ax=ax1)
    ax2 = fig.add_subplot(212)
    fig = sm.graphics.tsa.plot_pacf(data,lags=lag, ax=ax2)
    if not savefig:
        plt.show()
    else:
        plt.savefig(savename, dpi=200)

# loop through all current products
for column in cur_prod:
    # print('Working on %s' %column)
    d = diff[column]
    if d == 0:
        data = dt_ana[column]
    else:
        data = dt_ana[column].diff(d).dropna()
    save_dir = os.path.join(acf_pacf_out, column + ' (diff ' + str(d) + ').png')
    plot_acf_pacf(data, True, save_dir)
    plt.close()

######################################################################
# calculate BIC to determine p and q
l = int(len(cur_prod) / 10)
pmax = l
qmax = l
bic = dict()

# loop through all current products
for column in cur_prod:
    print('Working on %s' %column)
    d = diff[column]
    data = dt_ana[column].astype(float) #
    bic_matrix = []
    for p in range(pmax + 1):
        tmp = []
        for q in range(qmax + 1):
            try:
                tmp.append(ARIMA(data, (p, d, q)).fit().bic)
            except:
                tmp.append(np.nan)
        bic_matrix.append(tmp)
    bic[column] = bic_matrix
    print('-' * 80)

# products with empty BIC series are submitted for manual determination of p & q
manual_check = []

for column in cur_prod:
    data = pd.DataFrame(bic[column])
    if int(data.isnull().sum().sum()) == (l + 1) ** 2:
        print('%s is empty and should be manually checked. ' %column)
        manual_check.append(column)

machine_run = [x for x in cur_prod if x not in manual_check]

# retrieve p and q
p_q = dict()

for column in machine_run:
    data = pd.DataFrame(bic[column])
    p, q = data.stack().idxmin()
    p_q[column] = [p, q]

# store p, d, q for all available items
params = pd.DataFrame()
for column in machine_run:
    p = p_q[column][0]
    q = p_q[column][1]
    d = diff[column]
    params[column] = pd.Series([p, d, q])

######################################################################
# test the model(s)
lag = 6
validity = dict()
model = dict()

for column in machine_run:
    try:
        # predict
        arima = ARIMA(dt_ana[column].astype(float), tuple(params[column])).fit()
        predicted = arima.predict()
        #measure
        error = pd.Series(predicted) - dt_ana[column]
        lb, p = acorr_ljungbox(error, lags=1)
        h = (p < 0.05).sum() # valid model has all p > 0.05, i.e. h == 0
        if h > 0:
            validity[column] = False
            manual_check.append(column)
        else:
            validity[column] = True
            model[column] = arima
    except:
        # if it fails to predict at all, it is invalid
        validity[column] = False
        manual_check.append(column)

machine_run = [x for x in cur_prod if x not in manual_check]

params[machine_run].to_excel(mout)

######################################################################
# try out the models
forecast = dict()
start = pd.Timestamp(np.datetime64('2017-01'))
end = pd.Timestamp(np.datetime64('2017-12'))

#test
result = pd.concat([dt_ana[cc], amd.predict(start, end)])
ori = dt_ana[cc]
prd = amd.predict(start, end)

for column in machine_run:
    # predict
    ori = dt_ana[column]
    prt = dt_tst[column]
    prd = amd.predict(start, end)

    # plot
    plt.figure(figsize=(10,5))
    plt.title('Sales Projection of %s for %s - %s' %(cc, str(start)[:7], str(end)[:7]))
    plt_ori = plt.plot(ori, color='r', label='History', linestyle='-')
    plt_ori = plt.plot(prt, color='c', label='YTD', linestyle='-')
    plt_prd = plt.plot(prd, color='g', label='Projection', linestyle='--')
    plt.xlabel('Date')
    plt.ylabel('Sales Quantity')
    plt.legend(loc=0)

    # save
    fig_name = column + ' for ' + str(start)[:7] + ' - ' + str(end)[:7] + '.png'
    fig_path = os.path.join(out_path, fig_name)
    plt.savefig(fig_path, dpi=200)

    #close plot
    plt.close()


# Submit for supervisory inspection




















#
