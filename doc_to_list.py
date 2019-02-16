import sys
import re
from docx import Document


pmid_re = re.compile('PMID: (\d*)')


def process_document(document: Document):
    pmids = set()
    for para in document.paragraphs:
        text = para.text

        re_results = pmid_re.search(text)
        if re_results is None:
            continue

        pmid_groups = re_results.groups()
        if pmid_groups:
            for x in pmid_groups:
                pmids.add(int(x))

    for pmid in sorted(pmids):
        print(pmid)


if __name__ == '__main__':
    doc_file = sys.argv[1]
    process_document(Document(doc_file))
