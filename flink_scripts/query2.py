from pyflink.common.typeinfo import Types
from pyflink.datastream import DataStream
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaOffsetsInitializer, KafkaRecordSerializationSchema
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment

def query2():
        env = StreamExecutionEnvironment.get_execution_environment()
        #env.set_parallelism(1)
        
        #Setup kafka source
        source = KafkaSource.builder()\
                .set_bootstrap_servers('kafka:9092')\
                .set_topics('flink')\
                .set_group_id('flink')\
                .set_starting_offsets(KafkaOffsetsInitializer.earliest())\
                .set_value_only_deserializer(SimpleStringSchema())\
                .build()
                
        src = env.from_source(source, WatermarkStrategy.no_watermarks(), "Kafka Source")

        #Setup Kafka sink
        sink = KafkaSink.builder()\
                .set_bootstrap_servers('kafka:9092')\
                .set_record_serializer(KafkaRecordSerializationSchema.builder()\
                .set_topic('query1_out')\
                .set_value_serialization_schema(SimpleStringSchema())\
                .build())\
                .build()
        #Redirect input to output for testing TODO Remove
        src.sink_to(sink)
        env.execute()
        
        

if __name__ == '__main__':
        query2()
