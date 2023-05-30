from typing import List
import requests
from html.parser import HTMLParser
from dataclasses import dataclass



@dataclass
class Table:
    """
    Dataclass for a table extracted from the HTML page
    title is set by the last h2 / h3 element before the table
    headings are filled from <th> elements
    data are all str
    """
    title: str
    headings: List[str]
    rows: List[List[str]]


class TablesExtractor(HTMLParser):
    current_data: str = ""
    tables: List[Table] = [Table('', [], [[]])]
    current_row: List[str] = []

    def handle_endtag(self, tag: str):
        if tag == "br":
            return
        if tag == "a":
            return
        self.current_data = self.current_data.replace("\r\n", "")
        if tag in ("h2", "h3"):
            self.tables[-1].title = self.current_data
        if tag == "th":
            self.tables[-1].headings.append(self.current_data)
        if tag == "td":
            self.tables[-1].rows[-1].append(self.current_data)
        if tag == "tr":
            if self.tables[-1].rows[-1]:
                self.tables[-1].rows.append([])
        if tag == "table":
            self.tables.append(Table('', [], [[]]))
        self.current_data = ""

    def handle_data(self, data: str):
        self.current_data += data


def extract_tables(url: str) -> List[Table]:
    data = requests.get(url).text
    te = TablesExtractor()
    te.feed(data)
    te.tables.pop()
    return te.tables
