# VinuStorage

**VinuStorage** is a browser-based file vault for VinuChain. It packages one or more files into a ZIP archive, optionally encrypts the archive with AES-GCM, splits the bytes into transaction-sized chunks, and stores those chunks directly in VinuChain transaction calldata.

The result is a recoverable, on-chain file snapshot identified by a single index transaction hash.

![VinuStorage title](title.png)

## Features

- **No backend required** - the main app is a single `index.html` file.
- **On-chain file persistence** - file chunks are written into transaction calldata.
- **One-hash recovery** - recover the stored ZIP from the final index transaction hash.
- **Optional AES-GCM encryption** - encrypt before upload and decrypt during recovery.
- **Burner wallet mode** - generate a temporary wallet, fund it, upload, then sweep remaining VC back.
- **Custom key mode** - upload directly with your own private key when preferred.
- **Mainnet / testnet switch** - click the network widget to toggle between VinuChain mainnet and testnet RPCs.
- **Large archive support** - multipart index pages are used when the chunk list is too large for one index transaction.
- **Hardened recovery checks** - validates index format, transaction hashes, chunk order, and archive integrity before download.

## How It Works

1. Files selected in the browser are packed into a ZIP archive with JSZip.
2. If encryption is enabled, the ZIP bytes are encrypted with AES-GCM using a PBKDF2-derived key.
3. The payload is split into `120 KB` chunks.
4. Each chunk is sent as transaction calldata to the uploader wallet address.
5. VinuStorage creates a final index transaction containing:
   - the archive hash,
   - protocol mode (`V5_DIRECT` or `V5_MULTIPART`),
   - the ordered chunk transaction hashes.
6. Recovery starts from the index transaction hash, fetches all chunks, verifies SHA-256 integrity, and downloads a restored ZIP.

The browser app uses the protocol prefix:

```text
V5::VinuStorage_File::<fileHash>::<mode>::<payload>
```

## Quick Start

### Use the Web App

Because the app is a static frontend, you can open it directly:

```bash
git clone https://github.com/Vesflux/VinuStorage.git
cd VinuStorage
```

Then open `index.html` in a modern browser.

For the best local-browser behavior, you can also serve the folder with any static server:

```bash
python -m http.server 8080
```

Then visit:

```text
http://localhost:8080
```

### Send Files

1. Open the **SEND** tab.
2. Drag files into the drop zone, or click it to select files.
3. Choose an upload mode:
   - **Burner Wallet**: VinuStorage creates a temporary wallet and shows a funding QR/address.
   - **Custom Key**: paste a private key and upload directly from that wallet.
4. Optional: enable **AES-GCM Encryption** and set a password.
5. Enter the recipient VinuChain address.
6. Click **INITIALIZE VAULT**.
7. Save the final index transaction hash printed in the console.

### Recover Files

1. Open the **RECEIVE** tab.
2. Paste the index transaction hash.
3. If the archive was encrypted, enter the password.
4. Click **DECRYPT & RECOVER**.
5. The browser downloads a restored ZIP archive after integrity verification.

## Networks

The web app includes these RPC configurations:

| Network | RPC |
| --- | --- |
| VinuChain Mainnet | `https://rpc.vinuchain.org` |
| VinuChain Testnet | `https://testnet-rpc.vinuchain.org` |
| VinuChain Testnet fallback | `https://vinufoundation-rpc.com` |

The default network is mainnet. Click the network badge in the bottom-right corner to toggle networks.

## Security Notes

- VinuStorage stores data in public blockchain transaction calldata. Use encryption for anything private.
- If you lose the encryption password, encrypted archives cannot be recovered.
- If you lose the index transaction hash, recovery becomes difficult because the chunk order is stored there.
- Burner wallet private keys are temporarily stored in browser `sessionStorage` so interrupted uploads can be detected within the current tab session. Closing the tab clears them.
- Custom key mode requires pasting a private key into the browser. Only use it in an environment you trust.
- CDN scripts are pinned with Subresource Integrity checks so modified third-party assets are blocked by the browser.
- Uploaded data may be permanent or very hard to remove once transactions are confirmed.

## Cost Notes

Every chunk is an on-chain transaction, so upload cost grows with file size. The app estimates the required VC amount in burner wallet mode, including a safety margin. Remaining funds are swept back to the recipient address after upload when possible.

For smaller, cheaper uploads, compress files before sending or upload only the minimum data you need to preserve.

## Repository Structure

```text
.
|-- index.html   # VinuStorage Pro web app
|-- icon.png     # app icon
|-- title.png    # title image used by the UI
|-- LICENSE      # GPL-3.0 license
`-- README.md
```

## License

This project is licensed under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for details.

## Author

Created by **Vesflux**.

- GitHub: [@Vesflux](https://github.com/Vesflux)
- X: [@baanhah](https://x.com/baanhah)
- Email: <vesflux@gmail.com>
