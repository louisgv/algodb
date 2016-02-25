from cassandra.query import SimpleStatement
from throwtable.RankingModel.db_dependency import DB_beans
from throwtable.AlgorithmNames.parseRosetta import search_pattern, trim_pattern, parser, get_standardized_lang
import re


class Task:
    """
        self.solutions: a list of implementations.
                        each entry in list is a map,
                            with keys:'language', 'content'
                        each entry in content has attribute 'type', 'content'
        self.task_name: a string
        self.task_summary: a list of sentences
        self.nodeslist: a list of mediawiki nodes from the page's text
    """
    def _parse_language_from_header(self, title):
        # e.g. '{{header|8th}}'
        matchHeader = re.compile(r".*?\{\{header\|(.+?)\}\}.*")
        result = matchHeader.match(title)
        return result and result.group(1).strip()

    # find the first commentary block and the first code block,
    # if match found, return (commentary, code, entirematch),
    # otherwise return (commentary, None, None).
    def parse_text(self, text):
        match = search_pattern.search(text)
        if match is None:
            return (text, None, None)

        return (match.group(1), match.group(3), match.group(0))

    def trim(self, commentary):
        commentary = re.sub(trim_pattern, '', commentary).strip()
        # print '------'
        # print 'commentary', commentary
        return commentary

    def _parse_solutions(self, solution_nodes):
        self.solutions = list()
        current_solution = None
        for node in solution_nodes:
            # print '================================node: ', \
                # node.encode('utf8'), \
                # 'task:', self.task_name
            # print type(node)
            if type(node) is parser.nodes.heading.Heading:
                lang = \
                    self._parse_language_from_header(node.title.encode('utf8').strip())
                if lang is None:
                    print 'ERROR: WE ARE SCREWED!!', node
                    break
                if current_solution is not None:
                    self.solutions.append(current_solution)
                current_solution = dict()
                current_solution['language'] = \
                    get_standardized_lang(lang, self.db.rd)
                current_solution['content'] = list()
            if type(node) is parser.nodes.tag.Tag and node.tag == 'lang':
                current_solution['content'].append({'type': 'code',
                    'content': node.contents.encode('utf8')})
            if type(node) is parser.nodes.text.Text:
                text = str(node.value.encode('utf8'))
                (commentary, code, entirematch) = self.parse_text(text)
                while code is not None:
                    current_solution['content'].append({'type': 'code',
                        'content': code})
                    commentary = self.trim(commentary)
                    if len(commentary) > 0:
                        current_solution['content'].append({'type':
                            'commentary', 'content': commentary})
                    text = text[len(entirematch):]
                    (commentary, code, entirematch) = self.parse_text(text)

        # print '================================'

    def _parse_summary(self):
        self.task_summary = list()
        for i in range(len(self.nodeslist)):
            curr = self.nodeslist[i]
            if type(curr) is parser.nodes.heading.Heading:
                # print curr
                if self._parse_language_from_header(curr.title.encode('utf8')):
                    # print curr
                    self._parse_solutions(self.nodeslist[i:])
                    break
                else:
                    self.task_summary.append(curr.title.encode('utf8'))
            if type(curr) is parser.nodes.text.Text:
                self.task_summary.append(curr.value.encode('utf8'))

    def __init__(self, row, db):
        self.db = db
        self.nodeslist = parser.parse(row.text).nodes
        self.task_name = row.page_title
        self._parse_summary()

def get_all_tasks(db):
    """
        cas: cassandra session
        rd: redis connection
    """
    query = "SELECT * FROM rosettacode"
    statement = SimpleStatement(query, fetch_size=100)
    for row in db.cs_rs.execute(statement):
        process_single_impl(row, db)

def process_single_impl(row, db):
    task = Task(row, db)
    for solution in task.solutions:
        codes = []
        comments = []
        types = []

        for entry in solution['content']:
            if 'content' not in entry:
                print entry
            if entry['type'] == 'commentary':
                types.append(False)
                comments.append(entry['content'])
            elif entry['type'] == 'code':
                types.append(True)
                codes.append(entry['content'])

        db.cs_rs_impl.execute(
            """
            INSERT INTO impls (page_title, lang, categories, iwlinks, codes, comments, types)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            [row.page_title, solution['language'], row.categories, row.iwlinks,
                codes, comments, types]
        )

        print 'indexed:', row.page_title

def main():
    get_all_tasks(DB_beans())


if __name__ == '__main__':
    main()