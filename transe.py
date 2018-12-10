#!/usr/bin/env python3

import csv
from tqdm import tqdm
from pathlib import Path

import click
import networkx as nx
import scipy
from rdflib import Graph, Literal
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph


# def transform(entity):
#     if isinstance(entity, URIRef):
#         return entity
#     elif isinstance(entity, Literal):
#         if entity.datatype:
#             return f'{entity}^^{entity.datatype}'
#         else:
#             return f'{entity}'


# if __name__ == '__main__':
#     entities = set()
#     relations = set()
#     g = Graph()
#     g.parse("../data/dbpedia_small.ttl", format="nt")
#     for stmt in g:
#         entities.add(transform(stmt[0]))
#         entities.add(transform(stmt[2]))
#         relations.add(transform(stmt[1]))
#
#     with open('../data/entity_idx.csv', 'w', newline='\n') as csvfile:
#         csv_writer = csv.writer(csvfile, delimiter='\t',
#                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
#         for idx, elem in enumerate(entities):
#             csv_writer.writerow([elem, idx, ])
#
#     with open('../data/relation_idx.csv', 'w', newline='\n') as csvfile:
#         csv_writer = csv.writer(csvfile, delimiter='\t',
#                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
#         for idx, elem in enumerate(relations):
#             csv_writer.writerow([elem, idx, ])
#
#     print(len(entities))
#     print(len(relations))


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


if __name__ == '__main__':
    # to_sparse_matrix()
    cli()
