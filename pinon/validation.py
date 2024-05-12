class Validation:
    def __init__(self):
        print('Here')

    def run_validation(self):
        if self.all_ks is None:
            self.run_all_ks()

        for target_ticker in self.config.get_target_tickers():
            target_ks = self.all_ks.loc[target_ticker]
            peer_weights = self.config.get_peer_weights(target_ticker)

            for peer_ticker, peer_ks in target_ks.groupby(level=pn_cols.PEER_TICKER):
                peer_val = pd.DataFrame(columns=[pn_cols.TARGET_TICKER, pn_cols.K_QTR_PE,
                                               pn_cols.K_TTM_PE, pn_cols.MU_QTR_PRICE, pn_cols.PEER_WEIGHTS], index=peer_ks.index)


                # ROI calcs
                for (num_yrs, roi_ndx) in pn_cols.ROI_LIST:
                    if num_yrs > 0:
                        s = self.multiples.qtr_derived_bases.loc[(peer_ticker,), pn_cols.MU_QTR_PRICE].rolling(num_yrs * 4).apply(self.calc_roi, raw=False, args=(peer_ticker, num_yrs)).shift(-num_yrs * 4 - 1)
                    else:
                        l = len(self.multiples.qtr_derived_bases.loc[(peer_ticker,)])
                        s = self.multiples.qtr_derived_bases.loc[(peer_ticker,), pn_cols.MU_QTR_PRICE].rolling(l).apply(self.calc_roi, raw=False, args=(peer_ticker, l / 4)).shift(-l + 1)

                    peer_val.loc[(peer_ticker,), (roi_ndx,)] = s.values

                peer_val[pn_cols.TARGET_TICKER] = target_ticker
                peer_val[pn_cols.PEER_WEIGHTS] = peer_weights[peer_ticker]

                peer_val[pn_cols.MU_QTR_PRICE] = self.multiples.qtr_derived_bases.loc[peer_ticker, pn_cols.MU_QTR_PRICE]
                peer_val[pn_cols.K_TTM_PE] = np.empty((len(peer_val), 0)).tolist()
                peer_val[pn_cols.K_QTR_PE] = np.empty((len(peer_val), 0)).tolist()