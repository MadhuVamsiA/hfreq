"""
needs to be created for each pair in white list (not active one, for evry pair)
xrp_tg=new Trailing_Gain_Util('XRP/USDT');

xrp_tg.adjust_gain_profit(get_current_price())

   
need to add exchnage - worker.freqtrade.exchange

"""



class Trailing_Gain_Util:
    pair=None;
    trailing_gain_profit_percent=0.05;
    trailing_gain_profit=0;
    old_trailing_gain_profit=0;
    exchange=None;
    last_seen_current_price=None;
    last_seen_low_price=None;
    logger=None;
    #current_price=self.exchange.get_rate(self.pair, refresh=True, side="buy")
    #self.exchange.get_current_price(pair);


    def __init__(self,exchange,pair,logger,trailing_gain_profit_percent:float= 0.05):
        self.exchange=exchange;
        self.pair=pair;
        self.logger=logger
        self.trailing_gain_profit_percent=trailing_gain_profit_percent;
        self.last_seen_current_price=self.get_current_price();
        self.adjust_gain_profit(self.get_current_price(),self.trailing_gain_profit_percent,initial=True);
        
       
    def get_current_price(self):
        if self.exchange:
            self.last_seen_current_price=self.exchange.get_rate(self.pair, refresh=True, side="buy");
            return self.last_seen_current_price;
        else:
            return 0;

    def get_buy_flag(self):
        self.adjust_gain_profit(self.get_current_price(),self.trailing_gain_profit_percent);
        if self.trailing_gain_profit is not None and self.trailing_gain_profit < self.get_current_price():
            print(self);
            return True;
        else:
            print(self);
            return False;
        
    def adjust_gain_profit(self, current_price: float, trailing_gain_profit_percent,initial: bool = False) -> None:
            """
            This adjusts the stop loss to it's most recently observed setting
            :param current_price: Current rate the asset is traded
            :param stoploss: Stoploss as factor (sample -0.05 -> -5% below current price).
            :param initial: Called to initiate stop_loss.
                Skips everything if self.stop_loss is already set.
            """
            new_trailing_gain_profit = (float(current_price) + float(current_price * abs(trailing_gain_profit_percent)))
            print("new_trailing_gain_profit: ",new_trailing_gain_profit,"current_price: ",current_price);
            
            if initial and (self.trailing_gain_profit is None or self.trailing_gain_profit == 0):
                self.trailing_gain_profit=new_trailing_gain_profit;
                self.last_seen_low_price=current_price;
                self.logger.debug(f"{self.pair} - Assigning new trailing_gain_profit...")
                return


            # evaluate if the trailing_gain_profit needs to be updated
            else:
                if new_trailing_gain_profit < self.trailing_gain_profit:  # stop losses only walk up, never down!
                    self.logger.debug(f"{self.pair} - Adjusting trailing_gain_profit...")
                    print(" Adjusting trailing_gain_profit")
                    self.old_trailing_gain_profit=self.trailing_gain_profit;
                    self.trailing_gain_profit=new_trailing_gain_profit;
                    self.last_seen_low_price=current_price;
                
            
                else:
                    self.logger.debug(f"{self.pair} - Keeping current trailing_gain_profit...")

            
            self.logger.debug(
                f"{self.pair} - trailing_gain_profit adjusted. current_price={current_price:.8f}, "
                f"trailing_gain_profit={self.trailing_gain_profit:.8f}. "
                f"trailing_gain_profit helped in profit: "
                f"{float(self.old_trailing_gain_profit) - float(self.trailing_gain_profit):.8f}.")
            
            
    def __repr__(self):
        return (f'Trailing_Gain_Util(pair={self.pair}, trailing_gain_profit={self.trailing_gain_profit},old_trailing_gain_profit={self.old_trailing_gain_profit}, trailing_gain_profit_percent={self.trailing_gain_profit_percent}, last_seen_current_price={self.last_seen_current_price}, last_seen_low_price={self.last_seen_low_price})')