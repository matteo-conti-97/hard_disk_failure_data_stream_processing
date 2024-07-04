from pyflink.common.typeinfo import Types
from pyflink.datastream import DataStream
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaOffsetsInitializer, KafkaRecordSerializationSchema
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode, TimeCharacteristic
import sys
from pyflink.datastream.functions import MapFunction

class ParseCSVFunction(MapFunction):

    def map(self, line):
        # Split the CSV line into fields (adjust according to your CSV format)
        fields = line.split(",")

        # Assuming a simple CSV with two fields
        if len(fields) == 9:
            return (fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7], fields[8])
        else:
            # Handle if your CSV has different number of fields
            return ("Invalid", "CSV line")
class PrintFunction(MapFunction):
    def map(self, value):
        print(f"Record received: {value}")
        return value
    
def query1(win_type):
        env = StreamExecutionEnvironment.get_execution_environment()
        env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
        env.set_parallelism(1)
        env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
        env.get_config().set_latency_tracking_interval(5000)
        
        #Setup kafka source
        source = KafkaSource.builder()\
                .set_bootstrap_servers('kafka:9092')\
                .set_topics('flink')\
                .set_group_id('flink')\
                .set_starting_offsets(KafkaOffsetsInitializer.earliest())\
                .set_value_only_deserializer(SimpleStringSchema())\
                .build()
                
        

        #Setup Kafka sink
        sink = KafkaSink.builder()\
                .set_bootstrap_servers('kafka:9092')\
                .set_record_serializer(KafkaRecordSerializationSchema.builder()\
                .set_topic('query1_out')\
                .set_value_serialization_schema(SimpleStringSchema())\
                .build())\
                .build()
        
        #Redirect input to output for testing TODO Remove
        src = env.from_source(source, WatermarkStrategy.no_watermarks(), "Kafka Source")
        #parsed_stream = src.map(ParseCSVFunction(), output_type=Types.TUPLE([Types.STRING()] * 9))
        #parsed_stream.map(PrintFunction()).set_parallelism(1)
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
                
        query1(win_type)
