"""
Test Kafka Connectivity
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.kafka_config import KafkaProducerWrapper, get_kafka_consumer, TOPICS
import time


def test_producer():
    """Test Kafka producer"""
    print("Testing Kafka Producer...")
    
    producer = KafkaProducerWrapper()
    
    # Test message
    test_message = {
        'test': 'message',
        'timestamp': time.time()
    }
    
    success = producer.send_message(
        TOPICS['RIDE_REQUESTS'],
        test_message,
        key='test'
    )
    
    if success:
        print("✓ Producer test successful")
    else:
        print("✗ Producer test failed")
    
    producer.close()
    return success


def test_consumer():
    """Test Kafka consumer"""
    print("\nTesting Kafka Consumer...")
    
    try:
        consumer = get_kafka_consumer(
            TOPICS['RIDE_REQUESTS'],
            'test-group'
        )
        
        print("✓ Consumer connected successfully")
        print("  Waiting for messages (5 seconds)...")
        
        message_count = 0
        start_time = time.time()
        
        while time.time() - start_time < 5:
            messages = consumer.poll(timeout_ms=1000)
            for topic_partition, records in messages.items():
                message_count += len(records)
                for record in records:
                    print(f"  Received: {record.value}")
        
        print(f"✓ Received {message_count} message(s)")
        
        consumer.close()
        return True
        
    except Exception as e:
        print(f"✗ Consumer test failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("Kafka Connectivity Test")
    print("=" * 50)
    
    # Test producer
    producer_ok = test_producer()
    
    # Test consumer
    consumer_ok = test_consumer()
    
    print("\n" + "=" * 50)
    if producer_ok and consumer_ok:
        print("All tests passed!")
    else:
        print("Some tests failed. Check Kafka connection.")
    print("=" * 50)
