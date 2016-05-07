#!/usr/bin/env python3

import subprocess, os, sys

cmd = ['python3 modules/inverted_index_generator.py']
inverted_index_generator = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
inverted_index_generator.wait()

cmd = ['python3 modules/indexer.py']
indexer = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
indexer.wait()

cmd = ['python3 modules/query_processor.py']
query_processor = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
query_processor.wait()

cmd = ['python3 modules/search_engine.py']
search_engine = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
search_engine.wait()