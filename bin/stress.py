# -*- coding: utf-8 -*-

import json
import threading
import time
import sys
import os
import random
import string

from pyravendb.store import document_store

NUM_READ_THREADS = 80
NUM_WRITE_THREADS = 20
TIME_STRESS = 90

NUM_TEST = 0

URLS = ["http://172.17.0.2:8080", "http://172.17.0.3:8080", "http://172.17.0.4:8080"]
DATABASE = "pmd"

class Agregado (object):
    def __init__(self, json_obj):
        self.Agregado = json_obj

def randomString(stringLength):
    letters = string.ascii_letters + " "
    return ''.join(random.choice(letters) for i in range(stringLength))

def doc_read ():
    store = document_store.DocumentStore(urls = URLS, database = DATABASE)
    store.initialize()

    start = 0
    end = 0

    start = time.time()
    atual = time.time()
    i = 0

    while (atual - start) < TIME_STRESS:
        start_doc = time.time()

        with store.open_session() as session: 
            query_random = "FROM Agregadoes WHERE Agregado.name >= \"" + str (random.choice(string.ascii_uppercase)) + "\" SELECT Agregado "

            query_result = list(session.query(object_type=Agregado).raw_query(query_random))

        end_doc = time.time()

        interval_doc = end_doc - start_doc

        with open ("../logs/stress_single_doc_read_" + str(NUM_TEST) + ".csv", "a+") as fopen:
            fopen.write(str(NUM_TEST) + "\t" + str(interval_doc) + "\n")

        i += 1
        atual = time.time()

    end = time.time()

    interval = end - start

    with open ("../logs/stress_batch_read_" + str(NUM_TEST) + ".csv", "a+") as fopen:
        fopen.write(str(NUM_TEST) + "\t" + str(i) + "\t" + str(interval) + "\n")


def doc_update ():
    store = document_store.DocumentStore(urls = URLS, database = DATABASE)
    store.initialize()

    start = 0
    end = 0

    start = time.time()
    atual = time.time()
    i = 0
    
    while (atual - start) < TIME_STRESS:
        start_doc = time.time()

        with store.open_session() as session: 
            load_random = "agregadoes/" + str (1 + int (random.random() * 10000)) + "-B"
            load_result = session.load(load_random, object_type = Agregado)

            if isinstance(load_result, Agregado):
                load_result.Agregado["about"] = randomString (int (random.random() * 200)) + "\r\n"
                session.save_changes()

            else:
                with open ("../logs/stress_single_doc_write_fail" + str(NUM_TEST) + ".csv", "a+") as fopen:
                    fopen.write(str(NUM_TEST) + "\n")                
                continue

        end_doc = time.time()

        interval_doc = end_doc - start_doc

        with open ("../logs/stress_single_doc_write_" + str(NUM_TEST) + ".csv", "a+") as fopen:
            fopen.write(str(NUM_TEST) + "\t" + str(interval_doc) + "\n")

        i += 1
        atual = time.time()

    end = time.time()

    interval = end - start

    with open ("../logs/stress_batch_write_" + str(NUM_TEST) + ".csv", "a+") as fopen:
        fopen.write(str(NUM_TEST) + "\t" + str(i) + "\t" + str(interval) + "\n")        


if __name__ == '__main__':

    if (len(sys.argv) != 2):
        print ("Erro: Entre com o número do teste")
        sys.exit(0)

    NUM_TEST = sys.argv[1]

    start = time.time()

    threads = []

    for i in range (NUM_READ_THREADS):
        read_thread = threading.Thread(target = doc_read)
        threads.append(read_thread)

    for i in range (NUM_WRITE_THREADS):
        write_thread = threading.Thread(target = doc_update)
        threads.append(write_thread)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    end = time.time()

    print (end - start)