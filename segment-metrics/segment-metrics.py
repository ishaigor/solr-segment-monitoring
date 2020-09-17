import click
import dateutil.parser
import re
import requests

from datetime import datetime, timezone
from multidict import MultiDict
from statistics import median

from .models import cli_options

def print_prometheus_help(metric, help, type = 'gauge'):
    print("# HELP solr_%s metric for %s" % (metric, help))
    print("# TYPE solr_%s %s" % (metric, type))

# Print metrics in Prometheus format.
def print_prometheus_gauge(metric, help, values):
    print_prometheus_help(metric, help)
    for (labels, value) in values.items():
        if labels is None:
            print("solr_%s %f" % (metric, value))
        else:
            print("solr_%s{%s} %f" % (metric, labels, value))

# Print metrics in Prometheus format.
def print_prometheus_statistics(metric, help, values):
    print_prometheus_help('%s_min' % (metric), 'minimum of %s' % (help))
    print_prometheus_help('%s_max' % (metric), 'maximum of %s' % (help))
    print_prometheus_help('%s_median' % (metric), 'median of %s' % (help))
    print_prometheus_help(metric, help, 'summary')
    previous = None
    for labels in values.keys():
        if labels != previous:
            samples = values.getall(labels)
            count = len(samples)
            sample_sum = sum(samples)
            sample_min = min(samples)
            sample_max = max(samples)
            sample_median = median(samples)
            print("solr_%s_min{%s} %f" % (metric, labels, sample_min))
            print("solr_%s_max{%s} %f" % (metric, labels, sample_max))
            print("solr_%s_median{%s} %f" % (metric, labels, sample_median))
            print("solr_%s_sum{%s} %f" % (metric, labels, sample_sum))
            print("solr_%s_count{%s} %f" % (metric, labels, count))
            previous = labels

@click.command()
@cli_options.solr
@cli_options.cluster
def cli(solr, cluster):


    # define prometheus collectors
    segments = MultiDict()
    deleted_documents = MultiDict()
    documents = MultiDict()
    bytes = MultiDict()
    age = MultiDict()

    # query solr for collection metrics to get list of collections available
    response = requests.get(solr + 'admin/metrics?group=core&prefix=QUERY./select.errors')
    errors = response.json()

    # sample segment information for each collection and add to collectors
    for key in errors['metrics']:

        # get the name of the collection
        collection = re.sub(r'solr\.core\.(.+)\.shard.*.replica_.*', r'\1', key)

        # place a call for segment information
        response = requests.get(solr + collection + '/admin/segments?wt=json')
        segment_info = response.json()

        segment_label = "collection=\"%s\"" % (collection)

        segments[segment_label] = len(segment_info['segments'])


        for segment in segment_info['segments'].values():
            mergeCandidate = str(segment.get('mergeCandidate', False))
            source = segment['source']

            common_labels = "cluster=\"%s\",collection=\"%s\",source=\"%s\",mergeCandidate=\"%s\"" % (cluster, collection, source, mergeCandidate)

            # set samples
            deleted_documents.add(common_labels, segment['delCount'])
            documents.add(common_labels, segment['size'])
            bytes.add(common_labels, segment['sizeInBytes'])

            # set age
            created_at = dateutil.parser.parse(segment['age'])
            now = datetime.now(timezone.utc)
            age.add(common_labels, (now-created_at).total_seconds())

    print_prometheus_gauge('segments_total', 'total number of segments for the collection', segments)
    print_prometheus_statistics('segment_deleted_documents_total', 'total number of deleted documents in a segment', deleted_documents)
    print_prometheus_statistics('segment_documents_total', 'total number of documents in a segment', documents)
    print_prometheus_statistics('segment_bytes_total', 'total number of bytes in a segment', bytes)
    print_prometheus_statistics('segment_age_seconds', 'age of a segment in seconds comparing to now', age)

if __name__ == "__main__":
    cli()