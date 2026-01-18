import json, requests, os, zipfile, io, shutil, hashlib
from web3 import Web3


def join_and_extract(pieces_dir: str, dest_dir: str, expected_hash: str):
    os.makedirs(dest_dir, exist_ok=True)
    pieces = sorted([f for f in os.listdir(pieces_dir)])
    mem = io.BytesIO()
    for p in pieces:
        with open(os.path.join(pieces_dir, p), 'rb') as f:
            mem.write(f.read())

    full_data = mem.getvalue()
    actual_hash = hashlib.sha256(full_data).hexdigest()
    if actual_hash != expected_hash:
        if input("Unzip？(y/n)") != 'y': return

    mem.seek(0)
    try:
        with zipfile.ZipFile(mem, 'r') as zf:
            zf.extractall(dest_dir)
        print(f"Success! dir: {dest_dir}")
    except Exception as e:
        print(f"error: {e}")


def createFile():
    for h in tx:
        try:
            tx_data = w3.eth.get_transaction(h)
            input_data = tx_data['input']
            raw_payload = bytes.fromhex(input_data[2:])
            seq_num = raw_payload[:4].hex()
            file_bytes = raw_payload[4:]

            print(f'downloading: {seq_num}')
            with open(f'data/{seq_num}', 'wb') as f:
                f.write(file_bytes)
        except Exception as e:
            print(f"tx: {h} error: {e}")


if __name__ == '__main__':
    if os.path.exists('data'): shutil.rmtree('data')
    os.makedirs('data')

    w3 = Web3(Web3.HTTPProvider("https://testnet-rpc.vinuchain.org"))
    idx_hash = str(input("Index Hash>>")).strip()

    try:
        hex_blob = w3.eth.get_transaction(idx_hash)['input']
        s = bytes.fromhex(hex_blob[2:]).decode('utf-8')
        fromAddr, nonce_range, toAddr, ts, expected_hash = s.split("::")

        start_n, end_n = map(int, nonce_range.split('-'))
        print(f"from {fromAddr}, include {end_n - start_n}")

        scan_api = f'https://testnet.vinuexplorer.org/api/v2/addresses/{fromAddr}/transactions'
        req = requests.get(scan_api).json()
        tx = [i['hash'] for i in req['items'] if start_n <= i['nonce'] < end_n]
        tx.reverse()

        createFile()
        join_and_extract('data', 'out', expected_hash)
    except Exception as e:
        print(f"error:{e}")
