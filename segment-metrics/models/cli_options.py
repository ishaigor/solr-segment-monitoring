import os

from click import option

solr = option("--solr", help="Solr UI URL",
                   prompt="Solr UI URL (ex. http://<host>:<port>/solr/)", required=False)

cluster = option("--cluster", default="", help="Solr cluster",
                   prompt="Solr cluster (ex. your cluster label if collecting from multiple)", required=False)
