import psycopg2
from psycopg2.extras import DictCursor

import brazilian_business_partner_api

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


class PostgresSingletonDB:
    """Borg pattern singleton"""

    __state = {}

    def __init__(self, db_configs: None | dict = None):
        self.__dict__ = self.__state
        self.logger = brazilian_business_partner_api.Logger(log_name=__name__)
        self.connect(db_configs)

    def connect(self, db_configs):
        if not hasattr(self, "conn"):
            self.conn = psycopg2.connect(**db_configs)

            self.cur = self.conn.cursor(cursor_factory=DictCursor)
            self.cur.execute("SELECT VERSION()")

            self.logger.log.info(f"Connection established to: {self.cur.fetchone()[0]}")

    def execute(
        self, logger: brazilian_business_partner_api.Logger, query: str
    ) -> DictCursor:
        """Logged db query - returns the cursor object so caller can choose fetch method.
        Allowing caller to pass in their own logger.
        """
        logger.log.debug(f"Executing DB query: {query}")
        try:
            self.cur.execute(query)
            self.conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.log.debug("Error: %s" % error)
            self.conn.rollback()

        return self.cur
