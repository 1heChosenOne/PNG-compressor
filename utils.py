import os
import logging

logging.basicConfig(level=logging.DEBUG,format="%(asctime)s, %(name)s %(levelname)s, %(message)s")

def if_exists_delete(path_):
    if os.path.exists(path_):
        os.remove(path_)
    else:
        logging.error("if_exists_delete func couldn't find path to delete file")
        
        
    