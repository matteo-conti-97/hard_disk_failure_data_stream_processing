import sys
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors.kafka import (
    KafkaSource,
    KafkaSink,
    KafkaOffsetsInitializer,
    KafkaRecordSerializationSchema,
)
from pyflink.common.watermark_strategy import WatermarkStrategy, TimestampAssigner
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import (
    MapFunction,
    AggregateFunction,
    ProcessAllWindowFunction,
)
from pyflink.datastream.window import TumblingEventTimeWindows, GlobalWindows
from pyflink.datastream import StreamExecutionEnvironment

from pyflink.common import Time
from datetime import datetime
from operator import itemgetter

format = "%Y-%m-%dT%H:%M:%S.%f"


class OrderProcessFunction(ProcessAllWindowFunction):
    def process(self, content, elements):
        sorted_values = sorted(elements, key=itemgetter(2), reverse=True)
        top = (sorted_values[0][0], )
        for i in range(10):
            top = top + sorted_values[i][1:]
        return (top, )
 

class ParseCSVFunction(MapFunction):

    def map(self, line):
        # Split the CSV line into fields (adjust according to your CSV format)
        # Sline = line.replace("'", "")
        fields = line.split(",")
        if len(fields) == 39:
            if (
                fields[0] == "date"
                or fields[12] is None
                or fields[25] is None
                or fields[12] == ""
                or fields[25] == ""
                or fields[12] == " "
                or fields[25] == " "
            ):
                return "Invalid CSV line"
            # return (datetime.strptime(fields[0], format), fields[1], fields[2], int(fields[3]), int(fields[4]), float(fields[5]), float(fields[6]))
            return (
                datetime.strptime(fields[0], format),
                fields[1],
                fields[2],
                int(fields[3]),
                int(fields[4]),
                float(fields[12]),
                float(fields[25]),
            )
        else:
            # Handle if your CSV has different number of fields
            return "Invalid CSV line"


class PrintFunction(MapFunction):
    def map(self, value):
        print(f"Record received: {value}")
        return value


class FailureCounter(AggregateFunction):
    def create_accumulator(self):
        # Initialize the accumulator (date, vault_id, failure_count, serial_number_list, model_list)
        return (None, 0, 0, [])

    def add(self, value, accumulator):
        if accumulator[0] is None:
            if value[3] == 1:
                accumulator[3].append(value[1])
                accumulator[3].append(value[2])
            return (value[0], value[4], value[3], accumulator[3])

        if value[3] == 1:
            date = accumulator[0]
            vault_id = accumulator[1]
            sum = accumulator[2] + value[3]
            accumulator[3].append(value[1])
            accumulator[3].append(value[2])
            return (date, vault_id, sum, accumulator[3])
        else:
            return accumulator

    def get_result(self, accumulator):
        # Return the accumulator as the result
        return accumulator

    def merge(self, accumulator1, accumulator2):
        return

    def get_accumulator_type(self):
        # Define the data types of the accumulator
        return Types.TUPLE(
            [
                Types.SQL_DATE(),
                Types.INT(),
                Types.INT(),
                Types.LIST(Types.STRING()),
                Types.LIST(Types.STRING()),
            ]
        )

    def get_result_type(self):
        # Define the data type of the result
        return Types.TUPLE(
            [
                Types.SQL_DATE(),
                Types.INT(),
                Types.INT(),
                Types.LIST(Types.STRING()),
                Types.LIST(Types.STRING()),
            ]
        )


def tuple_to_csv_ser(tup):
    # Initialize an empty list to hold the string elements
    elements = []
    
    # Iterate through each element in the tuple and append it to the list
    for element in tup:
        if isinstance(element, datetime):
            elements.append(element.strftime('%Y-%m-%d'))
        else:
            elements.append(str(element))
    
    # Join the list elements into a single string separated by commas
    result = ','.join(elements)
    
    return result


class CustomTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value, record_timestamp):
        return int(value[0].timestamp() * 1000)


def query2(win):
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env.get_config().set_latency_tracking_interval(500)

    # Setup kafka source
    source = (
        KafkaSource.builder()
        .set_bootstrap_servers("kafka:9092")
        .set_topics("ingestion")
        .set_group_id("flink")
        .set_starting_offsets(KafkaOffsetsInitializer.earliest())
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    # Setup Kafka sink
    sink = (
        KafkaSink.builder()
        .set_bootstrap_servers("kafka:9092")
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic("query2_out")
            .set_value_serialization_schema(SimpleStringSchema())
            .build()
        )
        .build()
    )

    src = env.from_source(source, WatermarkStrategy.no_watermarks(), "Kafka Source")
    parsed_stream = (
        src.map(ParseCSVFunction())
        .filter(lambda x: x != ("Invalid CSV line"))
        .assign_timestamps_and_watermarks(
            WatermarkStrategy.for_monotonous_timestamps().with_timestamp_assigner(
                CustomTimestampAssigner()
            )
        )
        .map(
            lambda x: (x[0], x[1], x[2], x[3], x[4]),
            output_type=Types.TUPLE(
                [
                    Types.SQL_DATE(),
                    Types.STRING(),
                    Types.STRING(),
                    Types.INT(),
                    Types.INT()
                ]
            ),
        )
        .key_by(lambda x: x[4])
        .window(win)
        .aggregate(FailureCounter())\
        .window_all(win)\
        .process(OrderProcessFunction())
    )

    res = parsed_stream.map(lambda x: tuple_to_csv_ser(x), output_type=Types.STRING())
    # parsed_stream.map(PrintFunction())
    res.sink_to(sink)
    
    env.execute()


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Error in make command -> usage make run_query2 win_type=<win_type{1,2,3}={1day,3day,global}>"
        )
        exit()
    win_type = sys.argv[1]
    if win_type == str(1):
        print("Window size: One day")
        win = TumblingEventTimeWindows.of(Time.days(1))
    elif win_type == str(2):
        print("Window size: Three days")
        win = TumblingEventTimeWindows.of(Time.days(3), Time.days(2))
    elif win_type == str(3):
        print("Window size: Global")
        win = GlobalWindows.create()
    else:
        print("Invalid window size exiting...")
        exit()
    query2(win)
