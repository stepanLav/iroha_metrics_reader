import datetime
from prometheus_client.parser import text_string_to_metric_families
import time
import requests
import sys

HOSTNAME = ["http://localhost:3456", "http://localhost:3457", "http://localhost:3458", "http://localhost:3459"]

class Nodes():

    nodes = []
    max_block_height = 0
    max_block_diff = 0
    def __init__(self, urls):
        for node in urls:
            self.nodes.append(Node(node))

    def get_blocks_height(self):
        return_value = {}
        for node in self.nodes:
            return_value[node.url] = node.blocks_height
        return return_value

    def compare_blocks_height(self):
        for node in self.nodes:
            if (self.max_block_height < node.blocks_height):
                self.max_block_height = node.blocks_height
            compare = self.max_block_height - node.blocks_height
            if compare > self.max_block_diff:
                self.max_block_diff = compare
        print('{}\n   Max block height = {}\n   Current difference = {}\n   Max difference = {}'.format(datetime.datetime.now(), self.max_block_height, compare, self.max_block_diff))

    def update_node_data(self):
        for node in self.nodes:
            node.update_data()


class Node():
    def __init__(self, url):
        self.url = url
        self.blocks_height = 0
        self.number_of_signatures_in_last_block = 0
        self.total_number_of_transactions = 0

    def update_data(self):
        data = RequestToNode(self.url)
        for family in text_string_to_metric_families(data):
            for sample in family.samples:
                if (sample[0] == "blocks_height"):
                    self.blocks_height = sample[2]
                if (sample[0] == "number_of_signatures_in_last_block"):
                    self.number_of_signatures_in_last_block = sample[2]
                if (sample[0] == "total_number_of_transactions"):
                    self.total_number_of_transactions = sample[2]

def Average(lst):
    return sum(lst) / len(lst)

def RequestToNode(url):
    r =requests.get('%s/metrics' % url)
    return r.text

if __name__ == "__main__":
    # execute only if run as a script
    nodes = Nodes(HOSTNAME)
    while True:
        nodes.update_node_data()
        nodes.compare_blocks_height()