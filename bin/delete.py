# -*- coding: utf-8 -*-

import json
import _thread
import time
import sys
import os

from pyravendb.store import document_store

URLS = ["http://172.17.0.2:8080", "http://172.17.0.3:8080", "http://172.17.0.4:8080"]
DATABASE = "pmd"

def delete_thread (num_doc):
    store = document_store.DocumentStore(urls = URLS, database = DATABASE)
    store.initialize()

    id_doc = str(num_doc) + "-B"

    start = time.time()
    with store.open_session() as session: 
        session.delete("agregadoes/" + id_doc)
        session.save_changes()
    end = time.time()

    with open ("../logs/delete_single_doc.csv", "a+") as fopen:
        fopen.write(id_doc + "\t" + str (start) + "\t" + str(end) + "\t" + str(end - start) + "\n")

if __name__ == '__main__':
    for i in range (10000, 14500):
        delete_thread (i)
        # try:
        #     _thread.start_new_thread( delete_thread, (i, ) )
        # except:
        #     with open ("../logs/delete_thread_err.csv", "a+") as fopen:
        #         fopen.write(str (i) + "\n")