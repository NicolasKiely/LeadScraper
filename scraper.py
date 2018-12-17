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

print('Running')
