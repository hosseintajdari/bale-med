# چک‌لیست امنیت secretها (VPS)

این فایل برای جلوگیری از لو رفتن توکن بله، webhook secret، و رمز SSH است.

## هرگز در اینجا نگذارید

- `BALE_BOT_TOKEN`
- `BALE_WEBHOOK_SECRET`
- رمز SSH یا محتوای `~/.ssh/id_*`
- اسکرین‌شات از `.env` یا پنل VPS

## فقط روی سرور

```bash
/opt/bale-bot/.env
chmod 600 /opt/bale-bot/.env
```

مقادیر واقعی فقط در این فایل. در Git، چت، و issue عمومی نباشد.

## بعد از استقرار — بررسی سریع

```bash
# دسترسی فایل env
stat -c '%a' /opt/bale-bot/.env          # 600

# env در git نیست
cd /opt/bale-bot && git status --short .env   # خالی

# لاگ توکن/secret ندارد
sudo journalctl -u bale-bot -n 200 | grep -iE 'token|secret|BALE_BOT'
# خروجی خالی = خوب

# ارسال خاموش
grep BALE_ENABLE_SENDING /opt/bale-bot/.env   # false
```

## اگر secret لو رفت

1. توکن بله را در پنل ربات عوض کنید.
2. `BALE_WEBHOOK_SECRET` جدید در `.env` بگذارید.
3. `sudo systemctl restart bale-bot`
4. webhook را دوباره ثبت کنید: `bash deploy/scripts/08-register-webhook.sh`

## چه چیز از اینترنت دیده می‌شود؟

| مورد | عمومی؟ |
| --- | --- |
| توکن بله | خیر |
| webhook secret (به‌تنهایی) | خیر |
| `/health` | بله — فقط `{"status":"ok"}` |
| `/webhook/bale/{secret}` | فقط با secret درست |
| `/local/*` | خیر — Caddy برمی‌گرداند 404 |
| `chat_id` در JSON پاسخ webhook | خیر — در پاسخ عمومی حذف شده |
