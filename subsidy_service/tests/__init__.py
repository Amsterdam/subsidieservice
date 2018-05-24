from subsidy_service import config

config.Context.replace('subsidy_service/tests/subsidy_service_unittest.ini')

if 'subsidy_service_unittest.ini' not in config.Context._last_read:
    raise RuntimeError('Testing Context not loaded, aborting')
