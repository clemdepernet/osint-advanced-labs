# Environment report - <CASE-ID>

_Paste real command outputs. Screenshots are welcome but the text output is what gets graded._

## 1. Container / VM
| Check | Command | Output |
|---|---|---|
| Image used | `docker images osint-lab` | |
| Container hostname | `hostname` | |
| Timezone | `date +%Z` | |
| Locale | `echo $LANG` | |
| Disposable? (--rm) | `docker inspect -f '{{.HostConfig.AutoRemove}}' <name>` | |
| Workspace mount | `docker inspect -f '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}}' <name>` | |

## 2. Network exit
| Check | Command | Output |
|---|---|---|
| Direct exit IP + country | `curl -s https://ipinfo.io/json` | |
| Tor exit | `curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip` | |
| DNS resolver | `cat /etc/resolv.conf` | |

## 3. opsec_check.sh result
Paste the full output of `./opsec_check.sh --home-country <XX> --expect-tor`.
State whether the result is GO or NO-GO and what you fixed.

## 4. Browser fingerprint (persona browser profile)
| Site | Result | Comment |
|---|---|---|
| coveryourtracks.eff.org | unique? bits of identifying info? | |
| amiunique.org | unique? | |
| browserleaks.com/webrtc | local/public IP leaked? | |

## 5. Residual risks
What still leaks, and why you accept it (link to the OPSEC note).
