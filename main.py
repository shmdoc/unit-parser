# Created by Arno on 02/12/2019

# Source: https://stackoverflow.com/questions/3368969/find-string-between-two-substrings
import re

# Source: https://stackoverflow.com/questions/54059917/generate-all-length-n-permutations-of-true-false
import itertools

import sys

import escape_helpers


class Unit:
    name = ""
    notation = ""
    uri = ""
    definition = ""


supported_units = (
    "cm^3", "d", "degC", "degF", "degree_east", "degree_north", "g",
    "kg", "km", "l", "yr")

# html = open(sys.argv[1])  # The command line argument should point to this file: "units.html"
html = open("units.html")

unit_list = set()

lastReadUnit = None

sectionName = ""
prefPassed = False
failedlines = ""
failed = False
for line in html:
    if '<td class="conceptURI">' in line:
        lastReadUnit = Unit()
        parsed = re.search('<td class="conceptURI"><a href="(.*)">', line)
        try:
            lastReadUnit.uri = parsed.group(1)
        except:
            failed = True
            failedlines += line
    if '<td class="SN">' in line:
        parsed = re.search('<td class="SN">(.*)<a href=""></a></td>', line)
        try:
            lastReadUnit.definition = parsed.group(1)
        except:
            pass
    if '<td class="PREF">' in line:
        prefPassed = True
        parsed = re.search('<td class="PREF">(.*)<a href=""></a></td>', line)
        try:
            lastReadUnit.name = parsed.group(1)
        except:
            failed = True
            failedlines += line
    elif prefPassed and '<td class="ALT">' in line:
        prefPassed = False
        parsed = re.search('<td class="ALT">(.*)<a href=""></a></td>', line)
        try:
            lastReadUnit.notation = parsed.group(1)
        except:
            failed = True
            failedlines += line

        if not failed:
            if lastReadUnit.notation in supported_units:
                unit_list.add(lastReadUnit)
        else:
            failed = False

html.close()


def str_query(uri, relation, value):
    if value is not None:

        uri_relations = ("ext:unitUri")
        escaped_value = ""
        if relation in uri_relations:
            escaped_value = escape_helpers.sparql_escape_uri(value)
        else:
            escaped_value = escape_helpers.sparql_escape(value)

        if isinstance(value, bool):
            # Fix for weird problem with booleans
            escaped_value = escaped_value.replace("False", "false")
            escaped_value = escaped_value.replace("True", "true")
            escaped_value = escaped_value.replace("^^xsd:boolean",
                                                  "^^<http://mu.semte.ch/vocabularies/typed-literals/boolean>")

        return "\t\t{uri} {relation} {value} . \n".format(uri=uri, relation=relation,
                                                          value=escaped_value)
    return ""


# base_uri = "http://vocab.nerc.ac.uk/collection/P06/current/{id}/"

query_str = "INSERT DATA { \n"
query_str += "\tGRAPH {app_uri} {{ \n".format(
    app_uri=escape_helpers.sparql_escape_uri("http://mu.semte.ch/application"))
for unit in unit_list:
    uri = escape_helpers.sparql_escape_uri(unit.uri)
    print(unit.name, unit.notation, unit.uri)
    query_str += "\t\t{uri} a ext:Unit . \n".format(uri=uri)
    relation = "ext:unitName"
    query_str += str_query(uri, relation, unit.name)
    relation = "ext:unitNotation"
    query_str += str_query(uri, relation, unit.notation)
    relation = "ext:unitUri"
    query_str += str_query(uri, relation, unit.uri)
    relation = "ext:unitDefinition"
    query_str += str_query(uri, relation, unit.definition)
    relation = "mu:uuid"
    query_str += str_query(uri, relation, unit.uri[-5:-1])
query_str += "\t}\n"
query_str += "}\n"

prefixes = "PREFIX ext: {uri}\n".format(
    uri=escape_helpers.sparql_escape_uri("http://mu.semte.ch/vocabularies/ext/"))
prefixes += "PREFIX mu: {uri}\n".format(
    uri=escape_helpers.sparql_escape_uri("http://mu.semte.ch/vocabularies/core/"))
query_str = prefixes + query_str

# f = open(sys.argv[2], "w+")  # argv[2] should be cpp.json
f = open("query.sparql", "w+")
f.write(query_str)
f.close()

fails = open("error.log", "w+")
fails.write(failedlines)
fails.close()
