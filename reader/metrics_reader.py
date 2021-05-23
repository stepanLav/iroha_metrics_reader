from locust import HttpUser, task, between
from prometheus_client.parser import text_string_to_metric_families
from datetime import datetime
import sys

HOSTNAME = ["http://localhost:3451", "http://localhost:3452", "http://localhost:3453", "http://localhost:3454"]
current_block = 1.0
transactions = 0.0
need_incremet = bool(False)
start = datetime.now()
total_transaction = 0
avg_tps = []

class PrometheusListener(HttpUser):
    global HOSTNAME
    def __init__(self, *args, **kwargs):
        self.host = HOSTNAME.pop(0)
        super(PrometheusListener, self).__init__(*args, **kwargs)
    wait_time = between(5, 5)
    print(datetime.now, "Starting metrics")

    @task
    def get_metrics(self):
        response = self.client.get("/metrics")
        try:
            test = response.content.split(bytes("# HELP", 'utf-8'))
        except:
            print(datetime.now(), "Endpoint not answered, maybe node was restarted?")
        else:
            for line in test:
                if(line == b''):
                    continue
                else: result = b"# HELP" + line
                str_resultstr=(result.decode("utf-8"))
                for family in text_string_to_metric_families(str_resultstr):
                    for sample in family.samples:
                        global current_block
                        global need_incremet
                        global transactions
                        global start
                        global total_transaction
                        if (sample[0] == "blocks_height"):
                            if (current_block == 0):
                                current_block == sample[2]
                            if (current_block != sample[2]):
                                current_block = sample[2]
                                need_incremet = True
                        if (sample[0] == "number_of_signatures_in_last_block"):
                            if(need_incremet):
                                transactions += sample[2]
                                need_incremet = False
                        if (sample[0] == "total_number_of_transactions"):
                            if(total_transaction == 0):
                                total_transaction = sample[2]
                            calculate = (datetime.now()-start).total_seconds()
                            if(calculate > 10):
                                tps = (sample[2] - total_transaction)/10
                                total_transaction = sample[2]
                                start = datetime.now()
                                avg_tps.append(tps)
                                print('''=====================\nNow TPS is: {}\n=====================\n'''
                                .format(tps))
                                print('''\nAVG_TPS by last 100 sec. is: {}\n=====================\n'''
                                .format(Average(avg_tps)))
                                if (len(avg_tps) > 10):
                                    avg_tps.pop(0)

                        print("Name: {0} Labels: {1} Value: {2}".format(*sample))
            print(datetime.now(),"=========================================================", self.host)

def Average(lst):
    return sum(lst) / len(lst)

class LogToFile(object):
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout

    def __del__(self):
        self.close()

    def write(self, data):
        self.stdout.write(data)
        self.file.write(data)

    def flush(self):
        self.stdout.flush()
        self.file.flush()

    def close(self):
        if sys.stdout is self:
            sys.stdout = self.stdout
        self.file.close()


sys.stdout = LogToFile('log.txt', 'a')