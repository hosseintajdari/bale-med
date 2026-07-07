# DNS Setup for Milestone 8F and 8H

Bale webhooks require a **public HTTPS URL**. An IP address alone is not sufficient.

## Steps

1. Choose a hostname, e.g. `bot.yourpharmacy.ir`.
2. In your DNS provider, create an **A record**:
   - Name: `bot` (or `@` for apex)
   - Value: your VPS public IPv4
   - TTL: 300–3600 seconds (lower helps during first setup)
3. Wait for propagation (often 5–30 minutes; sometimes longer).
4. Verify from your laptop:

```bash
dig +short bot.yourpharmacy.ir A
curl -sI http://bot.yourpharmacy.ir
```

5. On the VPS after A record resolves:

```bash
export DOMAIN=bot.yourpharmacy.ir
sudo bash /opt/bale-bot/deploy/scripts/06-caddy.sh
```

Caddy will obtain a Let's Encrypt certificate automatically when ports 80 and 443 reach the server.

## If You Do Not Have a Domain Yet

You can complete **8A through 8E** without a domain. Pause before **8F** until DNS is ready.
