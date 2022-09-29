jupyter notebook --ip 0.0.0.0 --port 9999  --no-browser --NotebookApp.token='mirae123!' --allow-root



geth --datadir data --networkid 5777 --port 30303 -http --http.addr "0.0.0.0" --http.port 8505 --http.corsdomain "*" --http.api personal,eth,net,web3 console 2>> ./error.log


##curl
curl -X POST http://0.0.0.0:8505 -H "Content-Type:application/json" --data '{"jsonrpc":"2.0", "method":"eth_accounts","params":[], "id":1}'
eth.acc

### 기존 계정조회하기
a = requests.post("http://0.0.0.0:8505", headers = {"Content-Type":"application/json"}, data = '{"jsonrpc":"2.0","method":"eth_accounts","params":[],"id":1}')

## 신규계정만들기
a = requests.post("http://0.0.0.0:8505", headers = {"Content-Type":"application/json"}, data = '{"jsonrpc":"2.0","method":"personal_newAccount","params":["mirae123!"],"id":1}')

##블록개수조회
 a = requests.post("http://0.0.0.0:8505", headers = {"Content-Type":"application/json"}, data = '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}')
 

a = requests.post("http://0.0.0.0:8505", headers = {"Content-Type":"application/json"}, data = '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",false],"id":1}')


 geth --datadir data --networkid 5777 --port 30303 -http --http.addr "0.0.0.0" --http.port 8505 --http.corsdomain "*" --http.api personal,eth,net,web3 console 2>> ./error.log


## node 연결하기
 geth --datadir data --networkid 5777 --port 30303 -http --http.addr "0.0.0.0" --http.port 8505 --http.corsdomain "*" --http.api personal,eth,net,web3 console 2>> ./error.log

 geth --datadir data --networkid 5777 --port 30304 --authrpc.port 8552 -http --http.addr "0.0.0.0" --http.port 8506 --http.corsdomain "*" --http.api personal,eth,net,web3 console 2>> ./error.log


eth.getBalance(eth.coinbase)
web3.fromWei(eth.getBalance(eth.coinbase))
# 계정현황보기 
eth.accounts
web3.fromWei(eth.getBalance(eth.accounts[1]))
web3.fromWei(eth.getBalance(eth.accounts[eth.accounts.length-1]))
web3.fromWei(eth.getBalance(eth.accounts[5]))
# 이더주고받기
personal.unlockAccount(eth.accounts[0])
eth.sendTransaction({from: eth.accounts[1], to: eth.accounts[5], value: web3.toWei(10, "ether")})


eth.pendingTransactions

eth.blockNumber

#요기 다있네!! : https://cryptomarketpool.com/send-a-transaction-to-the-ethereum-blockchain-using-python-and-web3-py/