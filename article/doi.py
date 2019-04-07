import bs4
import typing

from article.article import BaseArticle
import author.author


class DoiArticle(BaseArticle):
    """ Processor for DOJ article """
    def get_journal(self):
        return 'DOI'

    def get_url(self) -> str:
        return self._reference_link

    def _get_archive_name(self) -> str:
        return 'archive/doi_%s.gzip' % self._pmid

    def get_linked_journals(
            self, doc_page: bs4.BeautifulSoup
    ) -> typing.List[BaseArticle]:
        return []

    def _get_authors(
            self, doc_page: bs4.BeautifulSoup
    ) -> typing.List[author.author.Author]:
        return []
