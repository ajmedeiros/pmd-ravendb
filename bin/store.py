# -*- coding: utf-8 -*-

import json
import _thread
import time
import sys
import os

from pyravendb.store import document_store

class Agregado (object):
    def __init__(self, json_obj):
        self.Agregado = json_obj

NUM_TEST = 0
NUM_FILE = 29
URLS = ["http://172.17.0.2:8080", "http://172.17.0.3:8080", "http://172.17.0.4:8080"]
DATABASE = "pmd"

def batch_thread ():
    for i in range (NUM_FILE):
        with open ("../raw_json/" + str(i) + ".json", 'r') as fopen:
            # Load batch from json file
            data = json.load (fopen)

            # Start a new thread with batch_job
            batch_job (data, i)


def batch_job (batch_json, num_file):
    store = document_store.DocumentStore(urls = URLS, database = DATABASE)
    store.initialize()

    start = 0
    end = 0

    start = time.time()

    for doc in batch_json:
        start_doc = time.time()

        with store.open_session() as session: 
            session.store(Agregado (doc))
            session.save_changes()

        end_doc = time.time()

        interval_doc = end_doc - start_doc

        with open ("../logs/store_single_doc.csv", "a+") as fopen:
            fopen.write(str(NUM_TEST) + "\t" + str(num_file) + "\t" + str(interval_doc) + "\n")

    end = time.time()

    interval = end - start

    with open ("../logs/store_batch_job.csv", "a+") as fopen:
        fopen.write(str(NUM_TEST) + "\t" + str(num_file) + "\t" + str(interval) + "\n")


if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print ("Erro: Entre com o número do teste")
        sys.exit(0)

    NUM_TEST = sys.argv[1]

    batch_thread()