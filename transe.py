#!/usr/bin/env python3

import csv
from tqdm import tqdm
from pathlib import Path

import click
import networkx as nx
import scipy
from rdflib import Graph, Literal
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph


@click.group()
def cli():
    pass


@cli.group(help='Preprocess files for TransE')
def preprocess():
    pass


@preprocess.command(help="Create index files from knowledge base dump (ttl)")
@click.argument('file')
def build_index_files(file):
    entities = set()
    relations = set()

    in_file = Path(file)
    in_dir = in_file.parent
    filename = in_file.name.replace(in_file.suffix, '')

    print("Reading RDF graph ...")
    g = Graph()
    g.parse(str(in_file), format="nt")
    for triple in g:
        if not isinstance(triple[2], Literal):
            entities.add(str(triple[0]))
            entities.add(str(triple[2]))
            relations.add(str(triple[1]))
    del g

    # sort entities and relations
    print('Sorting entities and relations')
    entities = sorted(entities)
    relations = sorted(relations)

    print("Converting RDF graph to data files ...")
    with open(f'{in_dir}/{filename}_entity_idx.csv', 'w', newline='\n') as entity_file, \
            open(f'{in_dir}/{filename}_relations_idx.csv', 'w') as relations_file:

        entity_writer = csv.writer(entity_file, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        relations_writer = csv.writer(relations_file, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for idx, elem in tqdm(enumerate(entities), desc='Writing entities', total=len(entities)):
            entity_writer.writerow([elem, idx, ])
        for idx, elem in tqdm(enumerate(relations), desc='Writing relations', total=len(relations)):
            relations_writer.writerow([elem, idx, ])


@preprocess.command(help="Create scipy sparse matrix")
@click.argument('file')
def to_sparse_matrix(file):
    in_file = Path(file)
    in_dir = in_file.parent
    filename = in_file.name.replace(in_file.suffix, '')

    print("Reading RDF graph ...")
    g = Graph()
    g.parse(str(in_file), format="nt")

    print("Converting RDF graph to NetworkX graph ...")
    netx_graph = rdflib_to_networkx_graph(g)
    del g  # free up some memory

    print("Converting NetworkX graph to Scipy sparse matrix format ...")
    graph_matrix = nx.to_scipy_sparse_matrix(netx_graph)
    del netx_graph  # free up some memory

    outfile = f'{str(in_dir)}/{filename}.npz'
    scipy.sparse.save_npz(outfile, graph_matrix)


@preprocess.command(help="Convert ttl file into tab separated file")
@click.argument('file')
@click.option('--entities_only', is_flag=True, help='removes all literals from the generated file')
def to_tab_separated(file, entities_only):
    """
    Converts a given ttl file into a tsv file.
    :param file: the ttl file to be converted
    :param entities_only: if True all literals will be removed.
    """
    in_file = Path(file)
    in_dir = in_file.parent
    filename = in_file.name.replace(in_file.suffix, '')

    print("Reading RDF graph ...")
    g = Graph()
    g.parse(str(in_file), format="nt")

    print("Converting RDF graph to tab separated file format ...")
    with open(f'{in_dir}/{filename}_triples.tsv', 'w', newline='\n') as f:
        writer = csv.writer(f, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        if entities_only:
            for s, p, o in tqdm(g, desc='Writing entities', total=len(g)):
                if not isinstance(o, Literal):
                    writer.writerow([s, p, o])
        else:
            for s, p, o in tqdm(g, desc='Writing entities', total=len(g)):
                writer.writerow([s, p, o])


if __name__ == '__main__':
    cli()
