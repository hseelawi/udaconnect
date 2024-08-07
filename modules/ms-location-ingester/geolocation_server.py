import grpc
from concurrent import futures
from kafka import KafkaProducer
import json
import logging
import geolocation_pb2
import geolocation_pb2_grpc
from configs import settings
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class GeoLocationService(geolocation_pb2_grpc.GeoLocationServiceServicer):
    def __init__(self, producer):
        self.producer = producer

    def SendLocation(self, request, context):
        # Convert Timestamp to datetime
        creation_time = datetime.fromtimestamp(
            request.creation_time.seconds + request.creation_time.nanos / 1e9
        )

        location_data = {
            "person_id": request.person_id,
            "longitude": request.longitude,
            "latitude": request.latitude,
            "creation_time": creation_time.isoformat(),
        }
        try:
            self.producer.send(settings.kafka_topic, location_data)
            logger.info(
                f"Location sent successfully for person_id: {request.person_id}"
            )
            return geolocation_pb2.LocationResponse(
                success=True, message="Location sent successfully"
            )
        except Exception as e:
            logger.error(
                f"Failed to send location for person_id {request.person_id}: {str(e)}"
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to send location: {str(e)}")
            return geolocation_pb2.LocationResponse(
                success=False, message=f"Failed to send location: {str(e)}"
            )


def serve():
    producer = KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    geolocation_pb2_grpc.add_GeoLocationServiceServicer_to_server(
        GeoLocationService(producer), server
    )
    server.add_insecure_port(f"[::]:{settings.grpc_server_port}")
    logger.info(f"Server started, listening on port {settings.grpc_server_port}")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server stopping...")
    finally:
        producer.close()
        logger.info("Kafka producer closed. Server stopped.")


if __name__ == "__main__":
    serve()
