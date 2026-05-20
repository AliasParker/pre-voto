# Services Inventory — pre.voto

External services used by the project. No secrets or API keys here — only public IDs and dashboard URLs.

| Servicio | Plan | Costo USD/mes | Dashboard | Variables de entorno |
|----------|------|---------------|-----------|---------------------|
| Hetzner (CPX22 Falkenstein) | Cloud VPS | ~$7 | https://console.hetzner.cloud | — |
| Cloudflare (DNS + TLS + WAF + cache) | Free | $0 | https://dash.cloudflare.com | — |
| Cloudflare R2 (backups) | Free tier | $0 | https://dash.cloudflare.com | `R2_*` |
| UptimeRobot | Free (50 monitors) | $0 | https://dashboard.uptimerobot.com | — |
| Beehiiv (newsletter) | Launch (free) | $0 | https://app.beehiiv.com | `BEEHIIV_API_KEY`, `BEEHIIV_PUBLICATION_ID`, `BEEHIIV_AUTOMATION_ID_CO` |
| Google Analytics 4 | Free | $0 | https://analytics.google.com | `PUBLIC_GA4_MEASUREMENT_ID=G-2ZPYJ7FQJV` |
| Stripe (donaciones) | Test mode | $0 (por ahora) | https://dashboard.stripe.com | Pendiente de configurar |
| Mercado Pago | Pendiente de activar | — | https://www.mercadopago.com.co/developers | Pendiente |
| GitHub (repo privado) | Free | $0 | https://github.com/AliasParker/Work-Space-Pre-Voto | — |

## Notas

- **Stripe** esta en test mode. Switch a live al momento de activar donaciones (PR 3).
- **Mercado Pago** esta pendiente de crear la cuenta de desarrollador en Colombia. No es bloqueante para el lanzamiento.
- **GA4** solo se activa si el usuario acepta el banner de cookies (Consent Mode v2).
- **Beehiiv** necesita los 3 custom fields (`top_match_name`, `top_match_pct`, `result_url`, `country`) y una automation antes de ser funcional.

## Variables de entorno adicionales (backend)

| Variable | Propósito | Dónde se configura |
|----------|-----------|-------------------|
| `ADMIN_PREVIEW_TOKEN` | Token para acceder a endpoints de preview de artículos no publicados | `.env` en backend |
