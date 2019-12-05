import os
import re

# Quick script to parse tables from the repl sql scripts
# Python 3.7.4

def parse_file_for_tables(file):
    results = []
    pattern = re.compile(r"^EXEC\ssys.sp_addarticle\s@publication\s=\sN'\w+',\s@article\s=\sN'(.*)',\s@source_owner")
    with open(file) as f:
        for line in f:
            match = re.match(pattern, line)
            try:
                results.append(match.group(1))
            except AttributeError:
                pass
    return results


def create_tables_list_file(file):
    file_out = "tables_for_" + file + ".txt"
    with open(file_out, "w") as f:
        tables = parse_file_for_tables(file)
        f.write('\n'.join(tables))


for file in ["repl.sql", "snaprepl.sql"]:
    create_tables_list_file(file)

