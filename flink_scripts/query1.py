import sys
from pyflink.common.typeinfo import Types
from pyflink.datastream import DataStream
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaOffsetsInitializer, KafkaRecordSerializationSchema
from pyflink.common.watermark_strategy import WatermarkStrategy, TimestampAssigner
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import MapFunction, AggregateFunction
from pyflink.datastream.window import TumblingEventTimeWindows, GlobalWindows
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode, TimeCharacteristic
from pyflink.common import Time
from datetime import datetime
from math import sqrt

format = "%Y-%m-%dT%H:%M:%S.%f"

class ParseCSVFunction(MapFunction):

    def map(self, line):
        # Split the CSV line into fields (adjust according to your CSV format)
        #Sline = line.replace("'", "")
        fields = line.split(",")
        if len(fields) == 39:
            if fields[0] == 'date' or fields[12] is None or fields[25] is None or fields[12] == '' or fields[25] == '' or fields[12] == ' ' or fields[25] == ' ':
                return ("Invalid CSV line")    
            #return (datetime.strptime(fields[0], format), fields[1], fields[2], int(fields[3]), int(fields[4]), float(fields[5]), float(fields[6]))
            return (datetime.strptime(fields[0], format), fields[1], fields[2], int(fields[3]), int(fields[4]), float(fields[12]), float(fields[25]))
        else:
            # Handle if your CSV has different number of fields
            return ("Invalid CSV line")
    
class PrintFunction(MapFunction):
    def map(self, value):
        print(f"Record received: {value}")
        return value

class EventCounter(AggregateFunction):
        def create_accumulator(self):
                # Initialize the accumulator (date, vault_id, temp, counter)
                return (None, 0, 0, 0.0, 0.0)

        def add(self, value, accumulator):
                # Update the accumulator with initial_date, current_vault_id, mean calculated with Welford online alghoritm, BiasedStdDeviation calculated with Welford online Alghoritm ,and increment the counter
                if accumulator[0] is None:
                        return (value[0], value[1], 1, value[2], 0.0)
                first_win_date = accumulator[0]
                vault_id = value[1]
                counter = accumulator[2] + 1
                old_mean = accumulator[3]
                old_std_dev = accumulator[4]
                new_mean = old_mean + ((value[2] - old_mean)/counter)
                new_bias_std_dev = old_std_dev + ((((value[2] - old_mean)*(value[2] - new_mean))-old_std_dev)/counter)
                return (first_win_date, vault_id,  counter, new_mean,  new_bias_std_dev)

        def get_result(self, accumulator):
                # Return the accumulator as the result
                return accumulator

        def merge(self, accumulator1, accumulator2):
             return

        def get_accumulator_type(self):
                # Define the data types of the accumulator
                return Types.TUPLE([
                Types.SQL_DATE(),
                Types.INT(),
                Types.INT(),
                Types.FLOAT(),
                Types.FLOAT()
                ])

        def get_result_type(self):
                # Define the data type of the result
                return Types.TUPLE([
                Types.SQL_DATE(),
                Types.INT(),
                Types.INT(),
                Types.FLOAT(),
                Types.FLOAT()
                ])


class CustomTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value, record_timestamp):
        return int(value[0].timestamp()*1000)
        
    
def query1(win):
        env = StreamExecutionEnvironment.get_execution_environment()
        env.set_parallelism(1)
        env.get_config().set_latency_tracking_interval(500)
                
        #Setup kafka source
        source = KafkaSource.builder()\
                .set_bootstrap_servers('kafka:9092')\
                .set_topics('ingestion')\
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
        
        
        src = env.from_source(source, WatermarkStrategy.for_monotonous_timestamps(), "Kafka Source")
        # parsed_stream = src.map(ParseCSVFunction(), output_type=Types.TUPLE(
        #         [Types.SQL_DATE(), 
        #          Types.STRING(), 
        #          Types.STRING(), 
        #          Types.INT(), 
        #          Types.INT(), 
        #          Types.FLOAT(), 
        #          Types.FLOAT()
        #          ]))\
        #         .assign_timestamps_and_watermarks(WatermarkStrategy\
        #                 .for_monotonous_timestamps()\
        #                 .with_timestamp_assigner(CustomTimestampAssigner()))\
        #         .map(lambda x: (x[0], x[4], x[6]), output_type=Types.TUPLE(
        #                 [Types.SQL_DATE(), 
        #                 Types.INT(), 
        #                 Types.FLOAT()
        #                 ]))\
        #         .key_by(lambda x: x[1])\
        #         .window(win).reduce(lambda x, y: (x[0], x[1], 1))
        parsed_stream = src.map(ParseCSVFunction())\
                .filter(lambda x: x != ("Invalid CSV line"))\
                .assign_timestamps_and_watermarks(WatermarkStrategy\
                        .for_monotonous_timestamps()\
                        .with_timestamp_assigner(CustomTimestampAssigner()))\
                .map(lambda x: (x[0], x[4], x[6]), output_type=Types.TUPLE(
                        [Types.SQL_DATE(), 
                        Types.INT(), 
                        Types.FLOAT()
                        ]))\
                .filter(lambda x: 1000 <= x[1] <=1020)\
                .key_by(lambda x: x[1])\
                .window(win).aggregate(EventCounter())\
                .map(lambda x: (x[0], x[1], x[2], x[3], sqrt(x[4])), output_type=Types.TUPLE(
                        [Types.SQL_DATE(),
                        Types.INT(),
                        Types.INT(), 
                        Types.FLOAT(),
                        Types.FLOAT()
                        ])
                )
                
                                               
        parsed_stream.map(PrintFunction())
        #parsed_stream.sink_to(sink)
        env.execute()
        
        

if __name__ == '__main__':
        if len(sys.argv) < 5:
                print("Error in make command -> usage make run_query1 win_type=<win_type{1,2,3}={1day,3day,global}>")
                exit()
        win_type=sys.argv[1]
        if win_type==str(1):     
                print("Window size: One day")
                win = TumblingEventTimeWindows.of(Time.days(1))
        elif win_type==str(2):
                print("Window size: Three days")
                win = TumblingEventTimeWindows.of(Time.days(3))
        elif win_type==str(3):
                print("Window size: Global")
                win = GlobalWindows.create()
        else:
                print("Invalid window size exiting...")
                exit()
                
        query1(win)
