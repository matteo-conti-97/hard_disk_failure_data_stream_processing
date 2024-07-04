from pyflink.common.typeinfo import Types
from pyflink.datastream import DataStream
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaOffsetsInitializer, KafkaRecordSerializationSchema
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
import sys

def query2(win_type):
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
        if len(sys.argv) < 5:
                print("Error in make command -> usage make run_query1 win_type=<win_type{1,2,3}={1day,3day,global}>")
                exit()
        win_type=sys.argv[1]
        if win_type==str(1):     
                print("Window size: One day")
        elif win_type==str(2):
                print("Window size: Three days")
        elif win_type==str(3):
                print("Window size: Global")
        else:
                print("Invalid window size exiting...")
                exit()
                
        query2(win_type)
