import datetime
import os, zipfile, io, shutil, hashlib
from time import sleep
from web3 import Web3

def get_sha256(data):
    return hashlib.sha256(data).hexdigest()

def zip_split_8digit(src_dir: str, out_dir: str, vol_kb: int = 126):
    if not os.path.exists(src_dir):
        raise FileNotFoundError(src_dir)
    os.makedirs(out_dir, exist_ok=True)
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(src_dir):
            for f in files:
                full = os.path.join(root, f)
                arc = os.path.relpath(full, src_dir)
                zf.write(full, arc)
    whole = mem.getvalue()
    file_hash = get_sha256(whole)
    vol_bytes = vol_kb * 1024
    tot = len(whole)
    start, idx = 0, 1
    while start < tot:
        chunk = whole[start:start + vol_bytes]
        name = f"{idx:08d}"
        with open(os.path.join(out_dir, name), 'wb') as fh:
            fh.write(chunk)
        start += vol_bytes
        idx += 1
    return file_hash


def createTX(num, n, max_retries=3):
    with open(f'data/{num}', 'rb') as f:
        msg_bytes = f.read()
    prefix = int(num).to_bytes(4, 'big')
    data_to_send = prefix + msg_bytes

    for i in range(max_retries):
        try:
            tx = {
                'nonce': n,
                'to': sender_addr,
                'value': 0,
                'gas': 2200000,
                'gasPrice': w3.eth.gas_price,
                'chainId': 206,
                'data': data_to_send.hex()
            }
            signed = w3.eth.account.sign_transaction(tx, private_key_hex)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            file_dict[num] = tx_hash.hex()
            print(f"[{num}] sent: {tx_hash.hex()}")
            return
        except Exception as e:
            print(f"[{num}] failed (try {i + 1}): {e}")
            sleep(2)


def qr_to_console(text):
    import qrcode
    qr = qrcode.QRCode(border=2)
    qr.add_data(text)
    qr.print_ascii(invert=True)


def indexTX(n, file_hash):
    data_str = f"{sender_addr}::{start_nonce}-{start_nonce + len(file_dict)}::{addr}::{datetime.datetime.utcnow().isoformat()}::{file_hash}"
    tx = {
        'nonce': n,
        'to': addr,
        'value': 0,
        'gas': 80000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 206,
        'data': data_str.encode('utf-8').hex()
    }
    tx_hash = w3.eth.send_raw_transaction(w3.eth.account.sign_transaction(tx, private_key_hex).rawTransaction)
    print(f"idx tx：{tx_hash.hex()}")


if __name__ == '__main__':
    if os.path.exists('data'): shutil.rmtree('data')
    os.makedirs('data')
    w3 = Web3(Web3.HTTPProvider("https://testnet-rpc.vinuchain.org"))

    with open('wallet.log', 'a') as f:
        private_key_hex = w3.eth.account.create().key.hex()
        sender_addr = w3.eth.account.from_key(private_key_hex).address
        f.write(f"\n[{datetime.datetime.utcnow()}] addr: {sender_addr} pk: {private_key_hex}")

    base = os.path.dirname(os.path.abspath(__file__))
    f_hash = zip_split_8digit(os.path.join(base, "file"), os.path.join(base, "data"), vol_kb=100)

    addr = str(input('addr>>'))
    file_names = sorted(os.listdir('data'))
    file_dict = {fname: None for fname in file_names}

    qr_to_console(sender_addr)
    needed = w3.fromWei(len(file_dict)*w3.eth.gas_price*2300000,'ether')
    print(f'{sender_addr} {w3.fromWei(len(file_dict)*w3.eth.gas_price*2300000+w3.toWei(0.01,"ether"),"ether")} VC')
    print("waiting...")
    while w3.fromWei(w3.eth.get_balance(sender_addr), 'ether') < needed:
        sleep(5)

    start_nonce = w3.eth.get_transaction_count(sender_addr)
    for i, fname in enumerate(file_names):
        createTX(fname, start_nonce + i)

    indexTX(start_nonce + len(file_dict), f_hash)
    print("Finsh！")

    sleep(60)
    for i in range(20):
        b_wei = w3.eth.get_balance(sender_addr) - w3.toWei(0.01, 'ether')
        if b_wei >= 0:
            tx = {
                'nonce': w3.eth.get_transaction_count(sender_addr),
                'to': addr,
                'value': b_wei,
                'gas': 50000,
                'gasPrice': w3.eth.gas_price,
                'chainId': 206,
            }
            tx_hash = w3.eth.send_raw_transaction(w3.eth.account.sign_transaction(tx, private_key_hex).rawTransaction)
            print(f"tx：", tx_hash.hex())
            break
        sleep(5)