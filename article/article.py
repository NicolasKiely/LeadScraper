import abc
import bs4
import gzip
import os
import time
import typing
import urllib.request

from author.author import Author


class BaseArticle(object):
    """ Base class for representing article data """
    def __init__(self, pmid: str, reference_link=None):
        self._pmid = pmid
        if reference_link is None:
            self._reference_link = self.get_url()
        else:
            self._reference_link = reference_link

    def load(self) -> str:
        """ Loads page data as string by pmid """
        archive_name = self._get_archive_name()
        if os.path.exists(archive_name):
            # File already downloaded, serve that
            return gzip.open(archive_name, 'r').read()

        else:
            # File not local, fetch from web
            time.sleep(0.5)
            response = urllib.request.urlopen(
                self.get_url(),
                timeout=self.timeout_limit
            )
            new_url = response.geturl()
            if new_url != self.get_url():
                print('\tRedirect %s -> %s' % (self.get_url(), new_url))

            with response:
                html_data = response.read()
                with gzip.open(archive_name, 'w') as fh:
                    fh.write(html_data)
                return html_data

    def process(self, html_data: str):
        """ Process html page, returning list of authors """
        if self.get_journal():
            print('\tJournal: %s' % self.get_journal())
        doc_page = bs4.BeautifulSoup(html_data, 'html.parser')
        linked_articles = self.get_linked_journals(doc_page)
        authors = []
        for linked_article in linked_articles:
            html_str = linked_article.load()
            authors += linked_article.process(html_str)

        if len(authors) == 0:
            # No authors found in linked journal
            authors = self._get_authors(doc_page)
        return authors

    @staticmethod
    def html_text(html_item):
        return ' '.join([
            s.replace('\n', ' ') for s in html_item.stripped_strings
            if s
        ])

    @property
    def timeout_limit(self):
        """ Timeout limit in seconds for downloading page """
        return 10

    @abc.abstractmethod
    def get_journal(self) -> str:
        pass

    @abc.abstractmethod
    def get_url(self) -> str:
        """ Implement in child. Return url """
        pass

    @abc.abstractmethod
    def _get_archive_name(self) -> str:
        """ Implement in child. Return archive name """
        pass

    @abc.abstractmethod
    def _get_authors(self, doc_page: bs4.BeautifulSoup) -> typing.List[Author]:
        """ Implement in child. Return list of authors """
        pass

    @abc.abstractmethod
    def get_linked_journals(
            self, doc_page: bs4.BeautifulSoup
    ) -> typing.List['BaseArticle']:
        """ Implement in child. Return linked journal article, if exists """
        pass
