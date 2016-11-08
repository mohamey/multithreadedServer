echo "Starting Server"
port=$1
echo $port
python3 server.py -p $port
