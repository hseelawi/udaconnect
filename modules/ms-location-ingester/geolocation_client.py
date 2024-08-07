import grpc
import logging
import random
from configs import settings
import geolocation_pb2
import geolocation_pb2_grpc
from shapely import wkb
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

# Set up logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

VALID_PERSON_IDS = [1, 5, 6, 8, 9]

# Locations and creation times from the seed db
COORDINATES_AND_TIMES = [
    ("010100000000ADF9F197925EC0FDA19927D7C64240", "2020-08-18 10:37:06.000000"),
    ("010100000097FDBAD39D925EC0D00A0C59DDC64240", "2020-08-15 10:37:06.000000"),
    ("010100000000ADF9F197925EC0FDA19927D7C64240", "2020-08-15 10:37:06.000000"),
    ("0101000000477364E597925EC0FDA19927D7C64240", "2020-08-15 10:37:06.000000"),
    ("0101000000477364E597925EC021787C7BD7C64240", "2020-08-19 10:37:06.000000"),
    ("010100000097FDBAD39D925EC0D00A0C59DDC64240", "2020-07-07 10:37:06.000000"),
    ("0101000000842FA75F7D874140CEEEDAEF9AA45AC0", "2020-07-07 10:37:06.000000"),
    ("0101000000842FA75F7D874140CEEEDAEF9AA45AC0", "2020-07-06 10:37:06.000000"),
    ("0101000000554FE61F7D87414002D9EBDD9FA45AC0", "2020-07-05 10:37:06.000000"),
    ("0101000000895C70067F874140CDB1BCAB9EA45AC0", "2020-04-07 10:37:06.000000"),
    ("0101000000895C70067F874140971128AC9EA45AC0", "2020-05-01 10:37:06.000000"),
    ("0101000000895C70067F874140CDB1BCAB9EA45AC0", "2020-07-07 10:38:06.000000"),
    ("0101000000895C70067F874140971128AC9EA45AC0", "2020-07-07 10:38:06.000000"),
    ("0101000000895C70067F874140971128AC9EA45AC0", "2020-07-01 10:38:06.000000"),
    ("0101000000842FA75F7D874140CEEEDAEF9AA45AC0", "2019-07-07 10:37:06.000000"),
    ("0101000000842FA75F7D874140CEEEDAEF9A645AC0", "2019-07-07 10:37:06.000000"),
    ("0101000000842FA75F7D074140CEEEDAEF9A645AC0", "2019-07-07 10:37:06.000000"),
    ("0101000000842FA75F7D874140DA0FC2ED9AA45AC0", "2020-07-05 10:37:06.000000"),
    ("0101000000842FA75F7D8741403A18FBDC9AA45AC0", "2020-01-05 10:37:06.000000"),
    ("010100000097FDBAD39D925EC0D00A0C59DDC64240", "2020-08-15 10:37:06.000000"),
]


def wkb_to_coordinates(wkb_str):
    point = wkb.loads(wkb_str)
    return point.x, point.y


def generate_location_data():
    for _ in range(settings.num_location_entries):
        wkb_str, creation_time_str = random.choice(COORDINATES_AND_TIMES)
        longitude, latitude = wkb_to_coordinates(wkb_str)
        creation_time = datetime.strptime(creation_time_str, "%Y-%m-%d %H:%M:%S.%f")
        yield {
            "person_id": random.choice(VALID_PERSON_IDS),
            "longitude": longitude,
            "latitude": latitude,
            "creation_time": creation_time,
        }


def run():
    try:
        with grpc.insecure_channel(settings.grpc_server_address) as channel:
            stub = geolocation_pb2_grpc.GeoLocationServiceStub(channel)
            for location in generate_location_data():
                timestamp = Timestamp()
                timestamp.FromDatetime(location["creation_time"])
                response = stub.SendLocation(
                    geolocation_pb2.LocationMessage(
                        person_id=location["person_id"],
                        longitude=location["longitude"],
                        latitude=location["latitude"],
                        creation_time=timestamp,
                    )
                )
                logger.info(
                    f"Client received for person {location['person_id']}: {response.message}"
                )
                logger.debug(
                    f"Response details for person {location['person_id']}: success={response.success}, message='{response.message}'"
                )
    except grpc.RpcError as e:
        logger.error(f"RPC failed: {e.code()}, {e.details()}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    run()
