import datetime
import logging
import pathlib
import sys
import tomllib as toml

import pandas as pd
import psycopg2
import psycopg2.extras as extras

import brazilian_business_partner_api
from brazilian_business_partner_api.connect import connect

_TOML = toml.load(
    open(str(pathlib.Path(__file__).parent.resolve() / "queries.toml"), "rb")
)

CHUNKS = 200
COUNT_QUERY = "SELECT COUNT(*) FROM {table}"
TRUNCATE_QUERY = "TRUNCATE TABLE {table}"
TABLE_EXISTS_QUERY = _TOML["table_exists"]
CREATE_STG_TABLE_DDL = _TOML["create_stage_table"]
DOT = "."
DB = "brazilian_business_partner_db"
STG_SCHEMA = "stage"
STG_TABLE = "company"
FQ_STG_TABLE = STG_SCHEMA + DOT + STG_TABLE


class Importer:
    """
    Class for importing data

    Args:
        config_file_path (Path): The path to the config file.
        csv_file_path(str): The full path of the csv file.
    Attributes:
        config_file_path (Path): The path to the config file.
        csv_file_path(str): The full path of the csv file.
        logger (brazilian_business_partner_api.Logger): Logger with a wrapper.
        destination_db(brazilian_business_partner_api.DB): An object to hold information about the connection to the destination DB
    """

    def __init__(self, csv_file_path, config_path: pathlib.Path, dbconfigs: dict):
        self.csv_file_path = csv_file_path
        self.config_path = config_path
        self.logger = brazilian_business_partner_api.Logger(log_name=__name__)
        self.destination_db = connect.PostgresSingletonDB(dbconfigs)

    def _bootstrap_needed(self, schematable: str) -> bool:
        """
        Determine if data needs to be loaded. If the main table doesn't have any data or does not exist, we will assume that we should
        also reload the stage table from the CSV.
        """
        if (
            self.destination_db.execute(
                self.logger,
                TABLE_EXISTS_QUERY.format(
                    table=schematable.split(".")[1],
                    schema=schematable.split(".")[0],
                ),
            ).fetchone()[0]
            == 0
        ):
            self.logger.info(
                f"""Stage table {schematable.upper()} doesn't exist. 
                Something weird must have occurred for this to happen, like a manual dropping of the table.  
                Will recreate and reload stage table."""
            )
            self.destination_db.execute(
                self.logger,
                CREATE_STG_TABLE_DDL.format(schematable=schematable),
            )
            return True

        return bool(
            self.destination_db.execute(
                self.logger, COUNT_QUERY.format(table=schematable)
            ).fetchone()[0]
            == 0
        )

    def _add_console_log_handler(self) -> None:
        formatter = logging.Formatter("%(message)s")
        self.ch = logging.StreamHandler(stream=sys.stdout)
        self.ch.set_name("console")
        self.ch.setLevel(level=logging.INFO)
        self.ch.setFormatter(formatter)
        self.logger.log.addHandler(self.ch)

    def _turn_off_console_handler(self) -> None:
        """
        Set to something super high so it will always _not_ write a message to be written to a log.
        Effectively turning it off.
        """
        console_level = 100
        self.ch.setLevel(console_level)

    def _truncate_stage_table(self, table) -> None:
        """
        Truncate table before inserting raw data
        """
        self.destination_db.execute(self.logger, TRUNCATE_QUERY.format(table=table))
        self.logger.log.debug(f"Stage table {table} truncated.")

    def _chunked_insert_to_stage(self, table: str, chunksize=None) -> None:
        """
        Inserts all the data into the stage table from the CSV.
        """
        self._truncate_stage_table(table)
        self._add_console_log_handler()
        self.logger.log.info(f"\n\n\n\tInserting rows into {table.upper()}...")

        if not chunksize:
            chunksize = self.csv_file_row_count // CHUNKS

        before = datetime.datetime.now()
        chunknum = 1
        prev_destination_db_row_count = 0
        with pd.read_csv(
            self.csv_file_path, header=0, sep="\t", dtype=str, chunksize=chunksize
        ) as reader:
            for chunked_df in reader:

                # compare row counts for validation when debugging
                df_num_rows = len(chunked_df.index)
                inserted_db_rows = 0

                # have to reorder df columns just so when 'execute_values()' is called,
                # force the same ordinal position for 'cols_str' and df columns
                sorted_col_list = sorted(list(chunked_df.columns))

                # replace default 'NaN' with NULLS to covnert to numpy array of tuples
                chunked_df = chunked_df[sorted_col_list].fillna(
                    psycopg2.extensions.AsIs("NULL")
                )
                tuples = [tuple(x) for x in chunked_df.to_numpy()]

                # prep insert query
                cols_str = ",".join([f'"{c}"' for c in sorted_col_list])
                INSERT_QUERY = "INSERT INTO %s(%s) VALUES %%s" % (table, cols_str)

                try:
                    extras.execute_values(self.destination_db.cur, INSERT_QUERY, tuples)
                    self.destination_db.conn.commit()

                    full_db_num_rows = self.destination_db.execute(
                        self.logger, COUNT_QUERY.format(table=table)
                    ).fetchone()[0]

                    inserted_db_rows = full_db_num_rows - prev_destination_db_row_count
                    assert df_num_rows == inserted_db_rows

                    prev_destination_db_row_count = full_db_num_rows
                    pct_done = round(
                        ((chunknum * chunksize) / self.csv_file_row_count) * 100, 1
                    )

                    # Print out every 5%
                    if CHUNKS >= 100:
                        if chunknum % ((CHUNKS // 100) * 2) == 0:
                            self.logger.log.info(
                                f"Table {table.upper()} --- {pct_done}% loaded..."
                            )
                    chunknum += 1

                except AssertionError as error:
                    self.logger.log.error(
                        f"""The dataframe is not inserted successfully. DF had {df_num_rows} rows. DBTable inserted {inserted_db_rows} rows.
                        Exception Thrown: {error}"""
                    )
                    self.destination_db.conn.rollback()

                except (Exception, psycopg2.DatabaseError) as error:
                    self.logger.log.debug("Error: %s" % error)
                    self.destination_db.conn.rollback()

        after = datetime.datetime.now()
        time_elapsed = after - before
        total_seconds = time_elapsed.total_seconds()
        mins = round(total_seconds / 60)
        seconds = round(total_seconds % 60, 1)
        self.logger.log.info(
            f"\nAll loaded! Total rows inserted into {table.upper()} - {prev_destination_db_row_count:,}. Elapsed time - {mins} mins and {seconds} seconds."
        )

        self.logger.log.info(
            f"\n\n\tTransformations are starting now. Check logs for progress..."
        )
        self._turn_off_console_handler()

    def _load_api_table(self, table: str) -> None:
        self.logger.log.debug(f"Table {table} populated.")

    def _ingest_csv(self, csv_file_path: str) -> None:
        """
        Read in full CSV without chunking
        """
        self.source_df = pd.read_csv(csv_file_path, header=0, sep="\t", dtype=str)

    def _count_rows_of_source_file(self) -> None:
        """
        Keep the row count in a instance variable
        """
        self.logger.log.debug(f"Counting source file rows...")
        count = 0
        with open(self.csv_file_path, "r") as fp:
            count = 0
            for line in fp:
                if line != "\n":
                    count += 1
        self.csv_file_row_count = count
        self.logger.log.debug(f"Source file '{self.csv_file_path}' has {count} rows.")

    def load(self, load_raw_data: bool, sample_size: int = 0) -> None:
        if not load_raw_data and not self._bootstrap_needed(FQ_STG_TABLE):
            self.logger.log.debug(f"Data already loaded. No bootstrap loading needed.")
            return

        self.logger.log.debug(f"No data in the stage table {STG_TABLE}.")
        self._count_rows_of_source_file()
        self._chunked_insert_to_stage(FQ_STG_TABLE)
