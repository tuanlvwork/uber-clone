"""
Kafka Configuration for Uber Clone
"""
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = [os.getenv('KAFKA_BOOTSTRAP_SERVERS', '127.0.0.1:9093')]

# Topic Names
TOPICS = {
    'RIDE_REQUESTS': 'ride-requests',
    'DRIVER_LOCATIONS': 'driver-locations',
    'DRIVER_AVAILABILITY': 'driver-availability',
    'RIDE_MATCHES': 'ride-matches',
    'RIDE_UPDATES': 'ride-updates',
}


def create_kafka_topics():
    """Create Kafka topics if they don't exist"""
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            client_id='uber-admin',
            # api_version=(2, 5, 0)
        )
        
        topic_list = [
            NewTopic(name=topic, num_partitions=3, replication_factor=1)
            for topic in TOPICS.values()
        ]
        
        try:
            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            logger.info("Topics created successfully")
        except Exception as e:
            if "TopicExistsException" in str(e):
                logger.info("Topics already exist")
            else:
                logger.error(f"Error creating topics: {e}")
        
        admin_client.close()
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")


def get_kafka_producer():
    """Create and return a Kafka producer"""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        # api_version=(2, 5, 0),
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None,
        acks='all',
        retries=3,
        max_in_flight_requests_per_connection=1
    )


def get_kafka_consumer(topic, group_id):
    """Create and return a Kafka consumer"""
    return KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        # api_version=(2, 5, 0),
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
        session_timeout_ms=30000,
        max_poll_interval_ms=300000
    )


class KafkaProducerWrapper:
    """Wrapper class for Kafka Producer with error handling"""
    
    def __init__(self):
        self.producer = None
        self.connect()
    
    def connect(self):
        """Connect to Kafka"""
        try:
            self.producer = get_kafka_producer()
            logger.info("Kafka producer connected")
        except Exception as e:
            logger.error(f"Failed to create Kafka producer: {e}")
            self.producer = None
    
    def send_message(self, topic, message, key=None):
        """Send message to Kafka topic"""
        if not self.producer:
            logger.warning("Producer not connected, attempting to reconnect...")
            self.connect()
        
        if self.producer:
            try:
                future = self.producer.send(topic, value=message, key=key)
                future.get(timeout=10)
                logger.info(f"Message sent to {topic}: {message}")
                return True
            except Exception as e:
                logger.error(f"Failed to send message to {topic}: {e}")
                return False
        return False
    
    def close(self):
        """Close the producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")


class KafkaConsumerWrapper:
    """Wrapper class for Kafka Consumer with error handling"""
    
    def __init__(self, topic, group_id, callback):
        self.topic = topic
        self.group_id = group_id
        self.callback = callback
        self.consumer = None
        self.running = False
    
    def connect(self):
        """Connect to Kafka"""
        try:
            self.consumer = get_kafka_consumer(self.topic, self.group_id)
            logger.info(f"Kafka consumer connected to {self.topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            return False
    
    def start_consuming(self):
        """Start consuming messages"""
        if not self.consumer and not self.connect():
            return
        
        self.running = True
        logger.info(f"Started consuming from {self.topic}")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    self.callback(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            self.close()
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self.running = False
        logger.info(f"Stopped consuming from {self.topic}")
    
    def close(self):
        """Close the consumer"""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")
