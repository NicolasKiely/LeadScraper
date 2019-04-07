import bs4
import typing

from article.article import BaseArticle
import author.author


def strip_mailto(email_str: str):
    mailto_str = 'mailto:'
    mailto_len = len(mailto_str)
    if email_str[:mailto_len] == mailto_str:
        return email_str[mailto_len:]
    return email_str


def is_affiliation(id_str: str):
    aff_str = 'authAffiliation'
    aff_len = len(aff_str)
    return id_str[:aff_len] == aff_str


def get_first_last_name(name_field: str):
    names = name_field.split(' ')
    if len(names) == 1:
        return '', names[0]
    else:
        return ' '.join(names[:-1]), names[-1]


class PlosOneArticle(BaseArticle):
    """ Processor for Plos ONE Journal """
    def get_journal(self) -> str:
        return 'Plos One'

    def get_url(self) -> str:
        return self._reference_link

    def _get_archive_name(self) -> str:
        return 'archive/plosone_%s.gzip' % self._pmid

    def get_linked_journals(
            self, doc_page: bs4.BeautifulSoup
    ) -> typing.List[BaseArticle]:
        return []

    def _get_authors(
            self, doc_page: bs4.BeautifulSoup
    ) -> typing.List[author.author.Author]:
        email_items = [
            item for item in doc_page.find_all(class_='email')
            if item.name == 'span'
        ]
        article_authors = []
        for email_item in email_items:
            email_parent = email_item.parent
            email_links = email_parent.find_all(name='a')
            if len(email_links) == 0:
                continue

            article_author = author.author.Author()
            article_author.source_article = self
            email_link = email_links[0]
            article_author.email = strip_mailto(email_link['href'])
            for child in email_parent.parent.parent.contents:
                if child is None or child.name is None:
                    continue

                if child.name == 'a' and 'author-name' in child['class']:
                    author_name = self.html_text(child)
                    first_name, last_name = get_first_last_name(author_name)
                    article_author.first_name = first_name
                    article_author.last_name = last_name
                    break

            for child in email_parent.parent.contents:
                if child.name == 'p' and is_affiliation(child['id']):
                    article_author.extra = self.html_text(child)
                    break

                article_authors.append(article_author)

        return article_authors
