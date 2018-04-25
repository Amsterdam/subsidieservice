import warnings
warnings.filterwarnings('ignore', message='\[bunq SDK')

import subsidy_service as service
import traceback
import time

subsidies = service.subsidies.read_all()


def remove_all_subsidies():
    for sub in subsidies:
        try:
            service.subsidies.delete(sub['id'])
            print('DELETED: Subsidy', sub['id'])
            time.sleep(1)  # don't hit rate limit
        except Exception as e:
            traceback.print_exc()
            print('ERROR: Could not delete subsidy', sub['id'])


def main():
    try:
        remove_all_subsidies()
    except service.exceptions.ForbiddenException:
        print('ERROR:', e.message)

if __name__ == '__main__':
    main()