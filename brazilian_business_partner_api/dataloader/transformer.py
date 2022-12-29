import pathlib
import tomllib as toml

import brazilian_business_partner_api
from brazilian_business_partner_api.connect import connect

_TOML = toml.load(
    open(str(pathlib.Path(__file__).parent.resolve() / "queries.toml"), "rb")
)

COUNT_QUERY = "SELECT COUNT(*) FROM {table}"
TRUNCATE_QUERY = "TRUNCATE TABLE {table}"
TABLE_EXISTS_QUERY = _TOML["table_exists"]
DOT = "."
DB = "brazilian_business_partner_db"
STG_SCHEMA = "stage"
TRANS_SCHEMA = "transformed"
STG_TABLE = "company"
COMPANY_TABLE = "dim_company"
XREF_TABLE = "xref_operator_company"
OPERATOR_TABLE = "dim_operator"
QUAL_TABLE = "dim_qualificacao_socio"
FQ_STG_TABLE = STG_SCHEMA + DOT + STG_TABLE
FQ_COMPANY_TABLE = TRANS_SCHEMA + DOT + COMPANY_TABLE
FQ_XREF_TABLE = TRANS_SCHEMA + DOT + XREF_TABLE
FQ_OPERATOR_TABLE = TRANS_SCHEMA + DOT + OPERATOR_TABLE
FQ_QUAL_TABLE = TRANS_SCHEMA + DOT + QUAL_TABLE
CREATE_COMPANY_TABLE_DDL = _TOML["create_dim_company"]
CREATE_COMPANY_INDEX_DDL = _TOML["create_dim_company_index"]
CREATE_OPERATOR_TABLE_DDL = _TOML["create_dim_operator"]
CREATE_OPERATOR_INDEX_DDL = _TOML["create_dim_operator_index"]
CREATE_QUAL_TABLE_DDL = _TOML["create_dim_qualificacao"]
CREATE_QUAL_INDEX_DDL = _TOML["create_dim_qualificacao_index"]
CREATE_XREF_TABLE_DDL = _TOML["create_dim_xref"]
CREATE_XREF_INDEX1_DDL = _TOML["create_dim_xref1_index"]
CREATE_XREF_INDEX2_DDL = _TOML["create_dim_xref2_index"]
INSERT_COMPANY_TABLE_QUERY = _TOML["insert_dim_company"]
INSERT_OPERATOR_TABLE_QUERY = _TOML["insert_dim_operator"]
INSERT_QUAL_TABLE_QUERY = _TOML["insert_dim_qualificacao"]
INSERT_XREF_TABLE_QUERY = _TOML["insert_dim_xref"]
REINDEX_SCHEMA_DDL = _TOML["reindex_schema"]


class Transformer:
    """
    Class for transforming data

    Args:
        config_file_path (Path): The path to the config file.
    Attributes:
        config_file_path (Path): The path to the config file.
        logger (brazilian_business_partner_api.Logger): Logger with a wrapper.
        destination_db(brazilian_business_partner_api.DB): An object to hold information about the connection to the destination DB
    """

    def __init__(self, config_path: pathlib.Path, dbconfigs: dict):
        self.config_path = config_path
        self.logger = brazilian_business_partner_api.Logger(log_name=__name__)
        self.destination_db = connect.PostgresSingletonDB(dbconfigs)

    def _create_if_table_not_exists(
        self,
        schematable: str,
        tableddl: str,
    ):
        """
        Queries information schema and creates table and the index (and secondindex if exists)
        if the table doesn't exist.

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

            self.destination_db.execute(
                self.logger,
                tableddl.format(schematable=schematable),
            )

    def _create_tables(self):
        self._create_if_table_not_exists(FQ_COMPANY_TABLE, CREATE_COMPANY_TABLE_DDL)
        self._create_if_table_not_exists(FQ_OPERATOR_TABLE, CREATE_OPERATOR_TABLE_DDL)
        self._create_if_table_not_exists(FQ_QUAL_TABLE, CREATE_QUAL_TABLE_DDL)
        self._create_if_table_not_exists(FQ_XREF_TABLE, CREATE_XREF_TABLE_DDL)

    def _create_indexes(self):
        self._create_indexes_on_each_table(FQ_COMPANY_TABLE, CREATE_COMPANY_INDEX_DDL)
        self._create_indexes_on_each_table(FQ_OPERATOR_TABLE, CREATE_OPERATOR_INDEX_DDL)
        self._create_indexes_on_each_table(FQ_QUAL_TABLE, CREATE_QUAL_INDEX_DDL)
        self._create_indexes_on_each_table(
            FQ_XREF_TABLE,
            CREATE_XREF_INDEX1_DDL,
            CREATE_XREF_INDEX2_DDL,
        )

    def _insert_into_table_if_empty(self, schematable: str, insertquery: str):

        if bool(
            self.destination_db.execute(
                self.logger, COUNT_QUERY.format(table=schematable)
            ).fetchone()[0]
            == 0
        ):
            self.logger.log.debug(
                f"{schematable.upper()} is empty, inserting rows now..."
            )

            self.destination_db.execute(
                self.logger,
                insertquery.format(schematable=schematable),
            )

            self.logger.log.debug(
                f"Done inserting into {schematable.upper()}. If no errors, it was successful."
            )

    def _create_indexes_on_each_table(
        self, schematable: str, indexddl: str, index2ddl: None | str = None
    ):

        self.logger.log.debug(f"Creating indexes on {schematable.upper()}.")
        self.destination_db.execute(
            self.logger,
            indexddl.format(schematable=schematable),
        )

        if index2ddl:
            self.destination_db.execute(
                self.logger,
                index2ddl.format(schematable=schematable),
            )

    def _insert_into_tables(self):
        self._insert_into_table_if_empty(FQ_COMPANY_TABLE, INSERT_COMPANY_TABLE_QUERY)
        self._insert_into_table_if_empty(FQ_OPERATOR_TABLE, INSERT_OPERATOR_TABLE_QUERY)
        self._insert_into_table_if_empty(FQ_QUAL_TABLE, INSERT_QUAL_TABLE_QUERY)
        self._insert_into_table_if_empty(FQ_XREF_TABLE, INSERT_XREF_TABLE_QUERY)

    def transform(self, transform_data: bool, sample_size: int = 0) -> None:
        self._create_tables()
        self._insert_into_tables()
        self._create_indexes()
