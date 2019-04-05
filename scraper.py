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
import csv
import sys

from article.pubmed import PubmedArticle


def first_last(authors: list):
    num_authors = len(authors)
    if num_authors == 0:
        return []

    elif num_authors == 1:
        return authors

    else:
        return authors[0], authors[-1]


def process_pmid(pmid: str, csv_results, empty_pmid_fh, no_journal_fh):
    print('Processing %s' % pmid)
    article = PubmedArticle(pmid)
    html_str = article.load()
    authors = first_last(article.process(html_str))

    if len(authors) == 0:
        empty_pmid_fh.write(article.get_url() + '\n')
    else:
        if all([a.journal == '' for a in authors]):
            no_journal_fh.write(article.get_url() + '\n')

    for author in authors:
        csv_results.writerow([
            pmid, author.journal, author.first_name, author.last_name,
            author.email, author.extra
        ])


print('Running')

if __name__ == '__main__':
    in_file_name = sys.argv[1]
    pmids = []
    with open(in_file_name, 'r') as in_fh:
        for pmid_record in in_fh:
            pmids.append(pmid_record.strip())

    with open('results.csv', 'w') as results_fh:
        empty_pmid_file = open('empty_pmids.txt', 'w')
        no_journal_file = open('no_journal.txt', 'w')

        results_writer = csv.writer(results_fh)
        results_writer.writerow(
            [
                'PMID', 'Journal', 'First Name', 'Last Name', 'E-mail',
                'Affiliation/Info',
            ]
        )
        for arg in pmids:
            process_pmid(arg, results_writer, empty_pmid_file, no_journal_file)

        empty_pmid_file.close()
        no_journal_file.close()
