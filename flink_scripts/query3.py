from pyflink.common.typeinfo import Types
from pyflink.datastream import DataStream
from pyflink.datastream.connectors.kafka import (
    KafkaSource,
    KafkaSink,
    KafkaOffsetsInitializer,
    KafkaRecordSerializationSchema,
)
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.watermark_strategy import WatermarkStrategy, TimestampAssigner
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import MapFunction, AggregateFunction
from pyflink.datastream.window import TumblingEventTimeWindows, GlobalWindows
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common import Time
import sys
from psquare.psquare import PSquare
from datetime import datetime
import math

format = "%Y-%m-%dT%H:%M:%S.%f"

def tuple_to_csv_ser(tup):
    # Initialize an empty list to hold the string elements
    elements = []

    # Iterate through each element in the tuple and append it to the list
    for element in tup:
        if isinstance(element, datetime):
            elements.append(element.strftime("%Y-%m-%d"))
        else:
            elements.append(str(element))

    # Join the list elements into a single string separated by commas
    result = ",".join(elements)

    return result


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

class CustomTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value, record_timestamp):
        return int(value[0].timestamp() * 1000)


class ComputePercentile(AggregateFunction):
    def create_accumulator(self):
        return (None, None, 0, float('inf') ,PSquare(25), PSquare(50), PSquare(75), 0, datetime.min.date()) # date, vault_id, count, min, 25th, 50th, 75th, max, max_date

    def add(self, value, acc):
        date = value[0] if acc[0] is None else acc[0]
        max_date = acc[8]
        if max_date < value[0]:
            max_date = value[0]
            pSquares = [PSquare(25), PSquare(50), PSquare(75)]
            for p in pSquares:
                p.update(value[3])
            return (acc[0], value[2], 1, value[3], pSquares[0], pSquares[1], pSquares[2], value[3], max_date)
        elif max_date > value[0]:
            return acc
        else:
            count = acc[2] + 1
            min_value = min(acc[3], value[3])
            acc[4].update(value[3])
            acc[5].update(value[3]) 
            acc[6].update(value[3])
            max_value = max(acc[7], value[3])
            
            return (
                    date,
                    value[2],
                    count,
                    min_value,
                    acc[4],
                    acc[5],
                    acc[6],
                    max_value,
                    max_date
            )

    def get_result(self, acc):
        return (
                acc[0],
                acc[1],    
                acc[2],
                acc[3],
                acc[4].p_estimate(),
                acc[5].p_estimate(),
                acc[6].p_estimate(),
                acc[7]
        )

    def merge(self, acc, acc1):
        return


    def get_result_type(self):
        # Define the data type of the result
        return Types.TUPLE(
            [Types.SQL_DATE(), Types.INT(), Types.INT(), Types.FLOAT(), Types.FLOAT(), Types.FLOAT(), Types.FLOAT(), Types.FLOAT()]
        )


def query3(win):
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

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
            .set_topic("query3_out")
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
            lambda x: (x[0], x[1], x[4], x[5]),
            output_type=Types.TUPLE(
                [Types.SQL_DATE(), Types.STRING(), Types.INT(), Types.FLOAT()]
            ),
        )
        .filter(lambda x: 1090 <= x[2] <= 1120)
        .key_by(lambda x: x[2])
        .window(win)
        .aggregate(ComputePercentile())
    )

    res = parsed_stream.map(lambda x: tuple_to_csv_ser(x), output_type=Types.STRING())
    #parsed_stream.map(PrintFunction())
    res.sink_to(sink)

    env.execute()


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Error in make command -> usage make run_query3 win_type=<win_type{1,2,3}={1day,3day,global}>"
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
    query3(win)
