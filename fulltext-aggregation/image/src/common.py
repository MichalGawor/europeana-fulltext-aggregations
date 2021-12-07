import os
import re
import logging
import unidecode

DEFAULT_OUTPUT_DIRECTORY = "./output"

CMD_NS = 'http://www.clarin.eu/cmd/1'
CMDP_NS = 'http://www.clarin.eu/cmd/1/profiles/clarin.eu:cr1:p_1633000337997'

EDM_NAMESPACES = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'ore': 'http://www.openarchives.org/ore/terms/',
    'edm': 'http://www.europeana.eu/schemas/edm/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dcterms': 'http://purl.org/dc/terms/',
}

CMD_NAMESPACES = {
    'cmd': CMD_NS,
    'cmdp': CMDP_NS
}

ALL_NAMESPACES = {**EDM_NAMESPACES, **CMD_NAMESPACES}

logger = logging.getLogger(__name__)


def id_to_filename(value):
    return value.replace('/', '_')


def get_mandatory_env_var(name):
    value = os.environ.get(name)
    if value is None:
        print(f"ERROR: mandatory {name} variable not set")
        exit(1)
    return value


def get_optional_env_var(name, default=None):
    value = os.environ.get(name)
    if value is None:
        return default
    else:
        return value


def get_metadata_dir(basedir, collection_id):
    return f"{basedir}/{collection_id}/metadata"


def get_fulltext_dir(basedir, collection_id):
    return f"{basedir}/{collection_id}/fulltext"


def xpath(tree, path, namespaces=ALL_NAMESPACES):
    return tree.xpath(path, namespaces=namespaces)


def xpath_text_values(tree, path, namespaces=ALL_NAMESPACES):
    nodes = xpath(tree, path, namespaces)
    if nodes is None:
        return []
    else:
        return [node.text for node in nodes]


def normalize_identifier(identifier):
    # ex. http://data.theeuropeanlibrary.org/BibliographicResource/3000118435146
    # ex. http://data.europeana.eu/annotation/9200396/BibliographicResource_3000118435009
    match = re.search(r"http.*[^\d](\d+)$", identifier)
    if match:
        logger.debug(f"Normalised identifier: {identifier} -> {match.group(1)}")
        return match.group(1)
    else:
        logger.warning(f"Identifier {identifier} does not match pattern, skipping normalisation!")
        return identifier


def xml_id(identifier):
    new_id = identifier
    if not re.match(r"^[A-z_]", identifier):
        new_id = "_" + identifier
    return re.sub('[^A-z0-9_]', '_', new_id)


def date_to_year(date):
    match = re.search(r"(\d{4})-\d{2}-\d{2}", date)
    if match:
        return match.group(1)
    else:
        return None


def is_valid_date(date):
    return re.match(r"(^\d{4})-\d{2}-\d{2}$", date) is not None


def normalize_title(title):
    match = re.search(r"^[A-z0-9'\"()\s]*[A-z0-9'\"()]", unidecode.unidecode(title))
    if match:
        return title[match.start(0):match.end(0)]
    else:
        return None


def filename_safe(name):
    return re.sub(r"[^A-z0-9]", '_', name)



def get_unique_xpath_values(docs, path):
    return list(dict.fromkeys(get_all_xpath_values(docs, path)))


def get_all_xpath_values(docs, path):
    values = []
    for doc in docs:
        values += xpath(doc, path)
    return values


def filter_fulltext_ids(ids, fulltext_dir):
    available_files = os.listdir(fulltext_dir)
    return list(filter(lambda identifier: id_to_fulltext_file(identifier) in available_files, ids))


def id_to_fulltext_file(identifier):
    return f"{id_to_filename(identifier)}.xml"
