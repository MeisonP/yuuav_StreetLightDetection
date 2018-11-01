
# coding: utf-8


from flask import Flask,request
import Link_GW
import logging
import time 
import json

def ini():
    TM=time.strftime("%Y-%m-%d %H-%M-%S",time.localtime())
    name='flask_app_log.txt'
    LOG_FORMAT = "%(asctime)s - %(levelname)s - [:%(lineno)d]- %(message)s"
    logging.basicConfig(filename=name,level=logging.INFO, format=LOG_FORMAT)
    logging.info('**************************Mason(%s):This is Flask*******************'%(TM,))

app = Flask(__name__)


@app.route('/process/')
def Baogan_project():
    arg=request.args.get('path')
    logging.info('Call model begin...')
    try:
        dictionary=Link_GW.main(arg)
    except:
        logging.error('model calling failed! ',exc_info=True)  
    logging.info('Call model done, begin to return data as jaon type.') 

    j= json.dumps(str(dictionary)) 
    return j



if __name__ == '__main__':

    ini()
    logging.info('Project func...waiting for image filename')
    app.run()

