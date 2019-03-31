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
import bs4
import csv
import gzip
import os
import sys
import time
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
        response = urllib.request.urlopen(PUBMED_URL % pmid, timeout=10)
        with response:
            html_data = response.read()
            with gzip.open(archive_name, 'w') as fh:
                fh.write(html_data)
            return html_data


def process_dl_list(dl):
    id_info_map = {}
    last_key = -1
    for item in dl.children:
        if item.name == 'dt' or item.name == u'dt':
            last_key = item.string
        else:
            id_info_map[last_key] = item.string
    return id_info_map


def process_auth_list(auths_div):
    id_auth_map = []
    last_name = ''
    for item in auths_div.children:
        if item.name == 'a' or item.name == u'a':
            last_name = item.string
        elif item.name == 'sup' or item.name == u'sup':
            id_auth_map.append((item.string, last_name))
    return id_auth_map


def get_email(record):
    fields = [s.strip() for s in record.split(' ')]
    for field in fields:
        if '@' in field:
            if field[0] != '@' and field[-1] != '@':
                return field
    return ''


def get_first_last_name(name_field):
    names = name_field.split(' ', 1)
    if len(names) == 1:
        return '', names[0]
    else:
        return names[1], names[0]


def process_pmid(pmid: str, csv_writer):
    print('Processing %s' % pmid)
    doc_page = bs4.BeautifulSoup(handle_pubmed_pmid(pmid), 'html.parser')
    auth_list_divs = doc_page.find_all(class_='auths')
    auth_names = None
    if len(auth_list_divs) > 0:
        auth_list_div = auth_list_divs[0]
        auth_names = process_auth_list(auth_list_div)

    auth_info_divs = doc_page.find_all(class_='afflist')
    auth_info = None
    if len(auth_info_divs) > 0:
        auth_info_div = auth_info_divs[0]
        auth_info = process_dl_list(auth_info_div.dl)

    if auth_names is None or auth_info is None:
        return

    for auth_id, auth_name in auth_names:
        auth_info_str = auth_info.get(auth_id, '')
        email = get_email(auth_info_str)
        first_name, last_name = get_first_last_name(auth_name)
        csv_writer.writerow([
            pmid, PUBMED_URL % pmid, first_name, last_name, email, auth_info_str
        ])


print('Running')

if __name__ == '__main__':
    in_file_name = sys.argv[1]
    pmids = []
    with open(in_file_name, 'r') as in_fh:
        for pmid_record in in_fh:
            pmids.append(pmid_record.strip())

    with open('results.csv', 'w') as results_fh:
        results_writer = csv.writer(results_fh)
        results_writer.writerow(
            ['PMID', 'Pubmed URL', 'First Name', 'Last Name', 'E-mail', 'Affiliation/Info',]
        )
        do_sleep = False
        for arg in pmids:
            if do_sleep:
                time.sleep(0.5)
            process_pmid(arg, results_writer)
            do_sleep = True
