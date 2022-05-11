import logging
import sys
from typing import Any, List

from freqtrade.commands import Arguments
#from freqtrade.exceptions import FreqtradeException, OperationalException
from freqtrade.loggers import setup_logging_pre


import os
os.chdir('E:\\madii\\h_freq\\freqtrade-stable')

print("setp 1 done");
#basic logger - will print to stdout  not to file
logger = logging.getLogger('freqtrade')
setup_logging_pre()

print("setp 2 done");

from freqtrade.worker import Worker
#arguments = Arguments(['trade'])

#arguments =  Arguments(['plot-dataframe', '-p', 'TLM/USDT', '--timeframe', '5m', '-v','--strategy','TechS'])

#arguments =  Arguments(['hyperopt', '--hyperopt-loss', 'SharpeHyperOptLossDaily', '--spaces', 'buy', 'sell','stoploss','trailing','--strategy','HyperStrategy','--config','hyper_config.json','-e','10','-j','3'])


#arguments = Arguments(['backtesting', '--strategy', 'SampleStrategyNew', '--timeframe', '1m'])

#arguments = Arguments(['trade','-c','no_loss_config.json','-v']);

#arguments = Arguments(['backtesting', '-c','no_loss_config.json', '--strategy', 'TGP_S', '--timeframe', '1m','--dry-run-wallet', '1000'])

#arguments = Arguments(['backtesting', '-c','no_loss_config.json', '--strategy', 'TGP_S_BT', '--timeframe', '1m','--dry-run-wallet', '1000'])


#arguments = Arguments(['logfile']) #logfile

arguments = Arguments(['trade'])
args = arguments.get_parsed_arg()

#args['strategy']='SampleStrategyNew'
print("setp 3 done");


import nest_asyncio
nest_asyncio.apply()
os.getcwd()
os.listdir()
print(args);

'''

args['strategy']='SampleStrategyNew'


{'command': 'backtesting',
 'verbosity': 0,
 'logfile': None,
 'config': ['user_data\\config.json'],
 'datadir': None,
 'user_data_dir': None,
 'strategy': None,
 'strategy_path': None,
 'timeframe': None,
 'timerange': None,
 'dataformat_ohlcv': None,
 'max_open_trades': None,
 'stake_amount': None,
 'fee': None,
 'pairs': None,
 'position_stacking': False,
 'use_max_market_positions': True,
 'enable_protections': False,
 'dry_run_wallet': None,
 'strategy_list': None,
 'export': None,
 'exportfilename': None,
 'func': <function freqtrade.commands.optimize_commands.start_backtesting(args: Dict[str, Any]) -> None>}


args= {'command': 'trade', 'verbosity': 0, 'logfile': None, 'config': ['user_data\\config.json'], 'datadir': None, 'user_data_dir': None, 'strategy': None, 'strategy_path': None, 'db_url': None, 'sd_notify': False, 'dry_run': False, 'dry_run_wallet': None, 'fee': None, 'func': <function start_trading at 0x000001D063D001F0>}
'''

#worker = Worker(args);
#worker.run()

#worker.exit();


return_code = args['func'](args)