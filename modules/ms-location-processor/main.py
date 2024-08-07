from datetime import datetime
import json
import logging
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from kafka import KafkaConsumer
from config import settings
from models import Base, Person, Location
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

# Set up logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the SQLAlchemy engine
db_params = settings.get_db_params()
engine = create_engine(URL.create(**db_params))

# Create all tables (this won't affect existing tables)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def process_message(message):
    data = json.loads(message.value)
    session = Session()
    try:
        person = session.query(Person).filter(Person.id == data["person_id"]).first()
        if not person:
            logger.warning(
                f"Person with id {data['person_id']} does not exist. Skipping location entry."
            )
            return

        # Use datetime.fromisoformat() instead of datetime.date.fromisoformat()
        creation_time = datetime.fromisoformat(data["creation_time"])

        location = Location(
            person_id=data["person_id"],
            coordinate=from_shape(
                Point(float(data["longitude"]), float(data["latitude"]))
            ),
            creation_time=creation_time,
        )
        session.add(location)
        session.commit()
        logger.info(f"Saved location entry for person {data['person_id']}")
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        session.rollback()
    finally:
        session.close()


def main():
    consumer = KafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="location_consumer_group",
        value_deserializer=lambda x: x.decode("utf-8"),
    )
    logger.info(f"Starting Kafka consumer on topic: {settings.kafka_topic}")
    logger.info(f"Using bootstrap servers: {settings.kafka_bootstrap_servers}")

    try:
        for message in consumer:
            process_message(message)
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
    finally:
        consumer.close()
        logger.info("Consumer closed, exiting.")


if __name__ == "__main__":
    main()
