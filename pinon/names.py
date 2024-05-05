import simfin.names as sf_cols

PAST_YEARS_REQUESTED = 'Past Years Requested'
TICKER = sf_cols.TICKER
COMPANY_NAME = sf_cols.COMPANY_NAME
INDUSTRY_ID = sf_cols.INDUSTRY_ID
REPORT_DATE = sf_cols.REPORT_DATE
TARGET_TICKER = 'Target Ticker'
PEER_TICKER = 'Peer Ticker'
EPS_BREAKING = 'EPS Breaking'
REVENUE_BREAKING = 'Revenue Breaking'
DIV_BREAKING = 'Dividend Breaking'
BREAKING_EMPLOYED = 'Breaking Report Employed'
QTR_EPS_FORECAST = 'Qtr EPS Forecast'
QTR_REV_FORECAST = 'Qtr Rev Forecast'
QTR_DIV_FORECAST = 'Qtr Div Forecast'
TTM_EPS_FORECAST = 'TTM EPS Forecast'
TTM_REV_FORECAST = 'TTM Rev Forecast'
TTM_DIV_FORECAST = 'TTM Div Forecast'
SIMFIN_SCHEMA = 'Simfin Schema'
WEIGHT = 'Weight'
PEER_WEIGHTS = 'Peer Weights'
PEER_LIST = 'Peer List'
EVALUATE = 'Evaluate'
LAST_REPORT_DATE = 'Last Report Date'
FIRST_REPORT_DATE = 'First Report Date'
PAST_YEARS_AVAILABLE = 'Past Years Available'
QTR_EPS = 'Quarterly EPS'
QTR_REV = 'Qtr Rev'
QTR_DIV = 'Qtr Div'
TTM_REV = 'TTM Rev'
TTM_DIV = 'TTM Div'
TTM_EPS = 'TTM EPS'
QTR_PE_RATIO = 'Quarterly PE Ratio'
TTM_PE_RATIO = 'TTM PE Ratio'
QTR_PE_FV = 'FV on Quarterly PE Ratio'
TTM_PE_FV = 'FV on TTM PE Ratio'
MU_QTR_PRICE = 'Mu Quarterly Price'
MU_QTR_PE_RATIO = 'Mu Quarterly PE Ratio'
MU_TTM_PE_RATIO = 'Mu TTM PE Ratio'
COMP_QTR_PE_RATIO = 'Comp Quarterly PE Ratio'
COMP_TTM_PE_RATIO = 'Comp Quarterly PE Ratio'
# K_QTR_PE = 'K_QTR_PE'
# K_TTM_PE = 'K_TTM_PE'
# K_QTR_PE = 'K_PEER_QTR_PE'
# K_TTM_PE = 'K_PEER_TTM_PE'
K_QTR_PE = 'K_TARGET_QTR_PE'
K_TTM_PE = 'K_TARGET_TTM_PE'
TIME_AVG = 'Time Averaged'
TIME_AVG_0_YEAR = '00 year'
TIME_AVG_1_YEAR = '01 year'
TIME_AVG_3_YEAR = '03 year'
TIME_AVG_5_YEAR = '05 year'
TIME_AVG_10_YEAR = '10 year'
TIME_AVG_MAX_YEAR = 'max year'
TIME_AVG_LIST = [(0, TIME_AVG_0_YEAR), (1, TIME_AVG_1_YEAR), (3, TIME_AVG_3_YEAR), (5, TIME_AVG_5_YEAR), (10, TIME_AVG_10_YEAR), (-1, TIME_AVG_MAX_YEAR)]
MU_TIME_LIST = ['0 year', '1 year', '3 year', '5 year']
UN_WTD_RATIOS = 'Unweighted Peers'
WTD_RATIOS = 'Weighted Peers'
WTD_ADJ_RATIOS = 'Weighted, Adjusted Peers'
TARGET_RATIOS = 'Target'
QTR_PE_RATIO_WTD = 'QTR_PE_RATIO_WTD'
TTM_PE_RATIO_WTD = 'TTM_PE_RATIO_WTD'
QTR_PE_RATIO_WTD_ADJ = 'QTR_PE_RATIO_WTD_ADJ'
TTM_PE_RATIO_WTD_ADJ = 'TTM_PE_RATIO_WTD_ADJ'
AROI_1_YEAR = 'AROI 1 year window'
AROI_3_YEAR = 'AROI 3 year window'
AROI_5_YEAR = 'AROI 5 year window'
AROI_10_YEAR = 'AROI 10 year window'
AROI_ALL_YEAR = 'AROI all year window'
ROI_LIST = [(1, AROI_1_YEAR), (3, AROI_3_YEAR), (5, AROI_5_YEAR), (10, AROI_10_YEAR), (-1, AROI_ALL_YEAR)]
