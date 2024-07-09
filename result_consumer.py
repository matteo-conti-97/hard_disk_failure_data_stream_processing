from confluent_kafka import Consumer
import time as Time
import sys

################
cons=Consumer({'bootstrap.servers':'localhost:9093','group.id':'csv_consumer','auto.offset.reset':'latest'})
print('Kafka Consumer has been initiated...')

################
head_query1="ts,vault_id,count,mean_s194,stddev_s194\n"
head_query2="ts,vault_id1,failures_1,[model_serial],vault_id2,failures_2,[model_serial],vault_id3,failures_3,[model_serial],vault_id4,failures_4,[model_serial],vault_id5,failures_5,[model_serial],vault_id6,failures_6,[model_serial],vault_id7,failures_7,[model_serial],vault_id8,failures_8,[model_serial],vault_id9,failures_9,[model_serial],vault_id10,failures_10,[model_serial]\n"
head_query3="ts,vault_id,count,min,25perc,50perc,75perc,max\n"
query_1_win_1_path="./results/query_1_win_1.csv"
query_1_win_3_path="./results/query_1_win_3.csv"
query_1_win_global_path="./results/query_1_win_global.csv"
query_2_win_1_path="./results/query_2_win_1.csv"
query_2_win_3_path="./results/query_2_win_3.csv"
query_2_win_global_path="./results/query_2_win_global.csv"
query_3_win_1_path="./results/query_3_win_1.csv"
query_3_win_3_path="./results/query_3_win_3.csv"
query_3_win_global_path="./results/query_3_win_global.csv"

def main(query, window):
    file = None
    header = None
    if query == '1' and window == '1':
        file=open(query_1_win_1_path,'w')
        header=head_query1
        cons.subscribe(['query1_out'])
    elif query == '1' and window == '3':
        file=open(query_1_win_3_path,'w')
        header=head_query1
        cons.subscribe(['query1_out'])
    elif query == '1' and window == 'global':
        file=open(query_1_win_global_path,'w')
        header=head_query1
        cons.subscribe(['query1_out'])
    elif query == '2' and window == '1':
        file=open(query_2_win_1_path,'w')
        header=head_query2
        cons.subscribe(['query2_out'])
    elif query == '2' and window == '3':
        file=open(query_2_win_3_path,'w')
        header=head_query2
        cons.subscribe(['query2_out'])
    elif query == '2' and window == 'global':
        file=open(query_2_win_global_path,'w')
        header=head_query2
        cons.subscribe(['query2_out'])
    elif query == '3' and window == '1':
        file=open(query_3_win_1_path,'w')
        header=head_query3
        cons.subscribe(['query3_out'])
    elif query == '3' and window =='3':
        file=open(query_3_win_3_path,'w')
        header=head_query3
        cons.subscribe(['query3_out'])
    elif query == '3' and window == 'global':
        file=open(query_3_win_global_path,'w')
        header=head_query3
        cons.subscribe(['query3_out'])
    else:
        print("Invalid query or window")
        return
    
    file.write(header)
    file.flush()
    print("Header written")
    
    start=Time.time()
    while Time.time()-start<8*60:   #8 minuti
        msg=cons.poll(1.0) #timeout
        if msg is None:
            continue
        if msg.error():
            print('Error: {}'.format(msg.error()))
            continue
        data=msg.value().decode('utf-8')
        start=Time.time()
        print(data)
        file.write(data+"\n")
        file.flush()
        continue
    
    cons.close()
    file.close()
    
if __name__ == '__main__':
    if(len(sys.argv)!=3):
        print("Usage: python3 result_consumer.py <query{1,2,3}> <window{1,3,all}>")
        sys.exit()
    query=sys.argv[1]
    window=sys.argv[2]
    main(query, window)