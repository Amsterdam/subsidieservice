'''
Created on 27 sep. 2018

@author: ricky
'''

import subsidy_service as service

def get_services_status():
    try:
        ctx = service.config.Context
        mc = ctx.mongo_client
        uri = mc._get_mongo_uri()
        service.mongo.get_collection(ctx.db.masters)
    except:
        return {"mongo", False, ""}
    return {"mongo", True, uri}
    
def get_endpoint_status():
    #TODO Implement the different endpoints with usual smoke actions.
    return {"daemon" : True}