<h1>
  <img src="icon.png" height="55" align="center">
  SubHunter
</h1>

SubHunter is a **subdomain enumeration and HTTP classification** tool designed for
reconnaissance and bug bounty workflows. It integrates multiple passive sources and
automatically classifies hosts based on their HTTP status codes.

## Features

- Subdomain enumeration using:
  - subfinder
  - assetfinder
  - findomain
  - sublist3r
- Automatic consolidation of **unique subdomains**
- HTTP probing and classification with httpx
- Separation by HTTP status code:
  - 200.txt
  - 301.txt
  - 403.txt
  - 404.txt
  - etc.
- Timeout detection
- Clean and organized output per target domain
- Designed for recon pipelines

---

## Requirements

Make sure the following tools are installed:

- Python 3.8+
- subfinder
- assetfinder
- findomain
- sublist3r
- httpx (ProjectDiscovery)

### Recommended installation (Go tools)

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/tomnomnom/assetfinder@latest
go install github.com/Findomain/Findomain@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
````

### Sublist3r installation

```bash
git clone https://github.com/aboul3la/Sublist3r.git
cd Sublist3r
pip3 install -r requirements.txt
sudo python3 setup.py install
```

Make sure `$HOME/go/bin` is included in your `$PATH`.

---

## Usage

```bash
python3 SubHunter.py example.com
```

---

## Output

```text
example.com/
 ├─ subdomains.txt     # all unique subdomains
 ├─ 200.txt            # hosts returning HTTP 200
 ├─ 301.txt
 ├─ 403.txt
 ├─ 404.txt
 └─ timeout.txt        # hosts with no HTTP response
```



