""" Pull in webpages from pubmed and save them to database

Foreach pmid entry in db:
    Is article in local archive?
        If not, download from pubmed
    Get authors and links from page
    Does article have links to original journal?
        If so, go to sourcing journal
        Is source journal article in archive?
            If not, download from source journal
        Get authors and links from source journal
    Save authors for journal, prioritizing original journal
"""
import gzip
import os
import sys
import urllib.request


#: Pubmed archive file name template
PUBMED_ARCHIVE_NAME = 'archive/pubmed_%s.gzip'
PUBMED_URL = 'https://www.ncbi.nlm.nih.gov/pubmed/%s'


def handle_pubmed_pmid(pmid: str):
    """ Handles top-level request to load pubmed article

    If article in local archive:
        Read from disk and serve up file
    else:
        Read from web, save to disk, then serve up file
    """
    archive_name = PUBMED_ARCHIVE_NAME % pmid
    if os.path.exists(archive_name):
        # File already downloaded, serve that
        return gzip.open(archive_name, 'r').read()
    else:
        # File not local, fetch from web
        response = urllib.request.urlopen(PUBMED_URL % pmid)
        with response:
            html_data = response.read()
            with gzip.open(archive_name, 'w') as fh:
                fh.write(html_data)
            return html_data


def process_pmid(pmid: str):
    print('Processing %s' % pmid)
    doc_page = handle_pubmed_pmid(pmid)
    print(doc_page)


print('Running')

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        process_pmid(arg)
