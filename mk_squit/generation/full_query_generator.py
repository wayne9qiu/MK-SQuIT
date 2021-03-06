# Copyright (c) 2020 MeetKai Inc. All rights reserved.

import os
import random
import itertools
from pathlib import Path

import typer
from tqdm import tqdm

from mk_squit.generation.predicate_bank import PredicateBank
from mk_squit.generation.template_filler import TemplateFiller
from mk_squit.generation.template_generator import TemplateGenerator
from mk_squit.generation.type_generator import TypeGenerator


class FullQueryGenerator(object):
    """Generates queries end-to-end."""

    def __init__(
        self,
        data_dir: str = "./data",
        property_file_identifier: str = "*-props-preprocessed.json",
        entity_file_identifier: str = "*-5k-preprocessed.json",
        type_list_file_name: str = "type-list-autogenerated.json",
    ):
        self.predicate_bank = PredicateBank(
            data_dir=data_dir,
            property_file_identifier=property_file_identifier,
            entity_file_identifier=entity_file_identifier,
            type_list_file_name=type_list_file_name

        )
        self.type_generator = TypeGenerator(predicate_bank=self.predicate_bank)

        self.template_generator = TemplateGenerator(
            type_generator=self.type_generator, predicate_bank=self.predicate_bank
        )

        self.template_filler = TemplateFiller(predicate_bank=self.predicate_bank)

    def generate_queries(self, n: int, out_file: str) -> None:
        """
        Args:
            n: the number of queries to generate
            out_file: the filename of the output file

        Generates n queries and writes them to out_file
        """
        all_queries = []
        for _ in tqdm(itertools.repeat(None, n)):
            for k, v in self.template_generator.templates.items():
                number_template = random.choice(v)
                type_template = self.template_generator.type_template(*number_template)
                if type_template is None:
                    continue
                filled_template = self.template_filler.fill_query(k, *type_template)
                if filled_template is None:
                    continue
                all_queries.append(filled_template)

        with open(out_file, "w") as f:
            f.write("english\tsparql\tunique hash\n")
            f.write("\n".join(["\t".join(exs) for exs in all_queries]))
            print(f"Saved to {out_file}")


def generate(
    data_dir: str = "data",
    prop_id: str = "*-props-preprocessed.json",
    ent_id: str = "*-5k-preprocessed.json",
    out_dir: str = "out"
):
    """Generate dataset end-to-end.

    python -m mk_squit.generation.full_query_generator \
        --data-dir data \
        --prop-id *-props-preprocessed.json \
        --ent-id *-5k-preprocessed.json \
        --out-dir out
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    query_generator = FullQueryGenerator(
        data_dir=data_dir, property_file_identifier=prop_id, entity_file_identifier=ent_id
    )
    query_generator.generate_queries(100000, os.path.join(out_dir, "train_queries_v3.tsv"))
    query_generator.generate_queries(5000, os.path.join(out_dir, "test_easy_queries_v3.tsv"))
    # query_generator.generate_queries(5000, os.path.join(out_dir, "test_hard_queries_v3.tsv"))     # TEST_HARD


if __name__ == "__main__":
    typer.run(generate)
