import time
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily, StateSetMetricFamily, InfoMetricFamily
from util.http_client import http_get_request
import dateutil.parser
import argparse
import datetime


class DkronMetricsController(object):
    def __init__(self, host, basic_auth_user, basic_auth_pass):
        self.host = host
        self.basic_auth_user = basic_auth_user
        self.basic_auth_pass = basic_auth_pass

    def collect(self):
        result = http_get_request("/v1/jobs", host=self.host, params=None, basic_auth_user=self.basic_auth_user,
                                  basic_auth_pass=self.basic_auth_pass)
        yield self.get_failure_metrics(result)
        yield self.get_success_metrics(result)
        yield self.get_last_exec_time_metrics(result)
        yield self.get_next_exec_time_metrics(result)
        yield self.get_status_metrics(result)
        yield self.get_info_metrics(result)
        yield self.get_schedule_status_metrics(result)

    def get_info_metrics(self, result):
        metric = InfoMetricFamily(
            'dkron_info',
            'Dkron job info',
            labels=["jobname"])

        for job in result:
            name = job['name']
            # If there's a null result, we want to export a zero.
            owner = job.get('owner')
            owner_email = job.get('owner_email')
            metric.add_metric([name], {'owner': owner, 'owner_email': owner_email})
            # job_status = job['status']
        return metric

    def get_status_metrics(self, result):
        metric = StateSetMetricFamily(
            'dkron_job_status',
            'Dkron job status',
            labels=["jobname"])

        for job in result:
            name = job['name']
            # If there's a null result, we want to export a zero.
            status = True
            status_txt = job.get('status') or 'failed'
            if status_txt == 'failed':
                status = False
            metric.add_metric([name], {'success': status})
            # job_status = job['status']
        return metric

    def get_schedule_status_metrics(self, result):
        metric = StateSetMetricFamily(
            'dkron_job_schedule_status',
            'Dkron job schedule status',
            labels=["jobname"])

        for job in result:
            name = job['name']
            # If there's a null result, we want to export a zero.
            next_date_str = job.get('next') or '2020-01-01T00:00:00.000Z'
            next_date = dateutil.parser.parse(next_date_str)
            diff_date = next_date - datetime.datetime.now(datetime.timezone.utc)
            if diff_date < datetime.timedelta(minutes=-1):
                metric.add_metric([name], {'success': False})
            else:
                metric.add_metric([name], {'success': True})
            # job_status = job['status']
        return metric

    def get_last_exec_time_metrics(self, result):
        metric = GaugeMetricFamily(
            'dkron_job_last_success_ts',
            'Dkron job last successful execution timestamp in unixtime',
            labels=["jobname"])

        for job in result:
            name = job['name']
            # If there's a null result, we want to export a zero.
            status = job.get('last_success') or '2020-01-01T00:00:00.000Z'
            d = dateutil.parser.parse(status)
            metric.add_metric([name], d.timestamp() / 1000.0)
            # job_status = job['status']
        return metric

    def get_next_exec_time_metrics(self, result):
        metric = GaugeMetricFamily(
            'dkron_job_next_exec_ts',
            'Dkron job next execution timestamp in unixtime',
            labels=["jobname"])

        for job in result:
            name = job['name']
            # If there's a null result, we want to export a zero.
            status = job.get('next') or '2020-01-01T00:00:00.000Z'
            d = dateutil.parser.parse(status)
            metric.add_metric([name], d.timestamp() / 1000.0)
            # job_status = job['status']
        return metric

    def get_failure_metrics(self, result):
        metric = CounterMetricFamily(
            'dkron_failure_counts',
            'Dkron job failure counts',
            labels=["jobname"])

        for job in result:
            name = job['name']
            # If there's a null result, we want to export a zero.
            status = job.get('error_count') or 0
            metric.add_metric([name], status)
            # job_status = job['status']
        return metric

    def get_success_metrics(self, result):
        metric = CounterMetricFamily(
            'dkron_job_success_count',
            'Dkron job success count',
            labels=["jobname"])

        for job in result:
            name = job['name']
            # If there's a null result, we want to export a zero.
            status = job.get('success_count') or 0
            metric.add_metric([name], status)
        return metric


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help='hostname e.g. https://jobs.helloworld.com')
    parser.add_argument("--basic_auth_user", help='Basic Authentication User Name')
    parser.add_argument("--basic_auth_pass", help='Basic Authentication Password')
    parser.add_argument("--port", help='port, default is 1234')
    args = parser.parse_args()

    host = args.host
    port = args.port or 1234
    REGISTRY.register(DkronMetricsController(host=host, basic_auth_user=args.basic_auth_user,
                                             basic_auth_pass=args.basic_auth_pass))
    start_http_server(int(port))
    while True: time.sleep(1)
