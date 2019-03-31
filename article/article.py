import abc
import gzip
import os
import urllib.request


PUBMED_ARCHIVE_NAME = 'archive/pubmed_%s.gzip'
PUBMED_URL = 'https://www.ncbi.nlm.nih.gov/pubmed/%s'


class BaseArticle(object):
    """ Base class for representing article data """
    def __init__(self, pmid: str):
        self._pmid = pmid

    def load(self) -> str:
        """ Loads page data as string by pmid """
        archive_name = self._get_archive_name()
        if os.path.exists(archive_name):
            # File already downloaded, serve that
            return gzip.open(archive_name, 'r').read()

        else:
            # File not local, fetch from web
            response = urllib.request.urlopen(
                self._get_url(),
                timeout=self.timeout_limit
            )
            with response:
                html_data = response.read()
                with gzip.open(archive_name, 'w') as fh:
                    fh.write(html_data)
                return html_data

    @property
    def timeout_limit(self):
        """ Timeout limit in seconds for downloading page """
        return 10

    @abc.abstractmethod
    def _get_url(self) -> str:
        """ Implement in child. Return url """
        pass

    @abc.abstractmethod
    def _get_archive_name(self) -> str:
        """ Implement in child. Return archive name """


class PubmedArticle(BaseArticle):
    """ Processor for pubmed articles """
    def _get_url(self) -> str:
        return PUBMED_URL % self._pmid

    def _get_archive_name(self) -> str:
        return PUBMED_ARCHIVE_NAME % self._pmid
