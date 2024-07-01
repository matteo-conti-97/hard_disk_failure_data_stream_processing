from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.descriptors import Schema, Csv

def query1():
        
        # Set up the execution environment
        env = StreamExecutionEnvironment.get_execution_environment()
        env.add_jars("file:///opt/flink/lib/flink-sql-connector-kafka-1.17.1.jar")
        
        t_env = StreamTableEnvironment.create(env)

        # Define Kafka source
        t_env.connect(
        Kafka()
        .version('universal')
        .topic('flink')
        .start_from_latest()
        .property('bootstrap.servers', 'kafka:9093')
        .property('group.id', 'flinkGroup')
        ).with_format(
                Csv()
                .derive_schema()
        ).with_schema(
        Schema()
                .field('date', DataTypes.DATE())
                .field('serial_number', DataTypes.STRING())
                .field('model', DataTypes.STRING())
                .field('failure', DataTypes.INT())
                .field('vault_id', DataTypes.INT())
                .field('s9_power_on_hours', DataTypes.FLOAT()) 
                .field('s194_temperature_celsius', DataTypes.INT())
        ).create_temporary_table('kafka_source')
        
        # Define the transformation
        table = t_env.from_path('kafka_source')
        result = table.select('user, message')
        env.execute()
        print(result)
        

if __name__ == '__main__':
        query1()


'''
# Define the Kafka sink table
t_env.create_temporary_table(
    'kafka_sink',
    TableDescriptor.for_connector('kafka')
        .schema(Schema.new_builder()
                .column('transaction_id', DataTypes.STRING())
                .column('customer_id', DataTypes.STRING())
                .column('product_id', DataTypes.STRING())
                .column('quantity', DataTypes.INT())
                .column('price', DataTypes.FLOAT())
                .build())
        .option('topic', 'sales_report_topic')
        .option('properties.bootstrap.servers', 'localhost:9092')
        .format(FormatDescriptor.for_format('json')
                .build())
        .build())'''