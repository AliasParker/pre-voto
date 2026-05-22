<script lang="ts">
  import { MessageCircle, Send, Link } from "lucide-svelte";
  import { t, type Locale } from "../../lib/i18n";

  interface Props {
    url: string;
    topCandidate: string;
    affinity: number;
    locale?: Locale;
  }

  let { url, topCandidate, affinity, locale = "es" }: Props = $props();

  let copied = $state(false);

  const shareText = $derived(
    t(locale, "results.shareText", { name: topCandidate, pct: String(affinity) })
  );

  const whatsappUrl = $derived(
    `https://wa.me/?text=${encodeURIComponent(shareText + " " + url)}`
  );

  const twitterUrl = $derived(
    `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(url)}`
  );

  const telegramUrl = $derived(
    `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(shareText)}`
  );

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(url);
      copied = true;
      setTimeout(() => (copied = false), 2000);
      if (typeof window !== "undefined" && (window as any).__pvEvent) {
        (window as any).__pvEvent("result_shared", { method: "copy_link" });
      }
    } catch {}
  }
</script>

<div class="border border-line rounded-xl p-5 bg-paper-warm/50">
  <!-- Header with pre.voto branding -->
  <div class="flex items-center gap-3 mb-3">
    <span class="text-lg font-bold tracking-tight">
      <span class="text-ink">pre</span><span class="text-brand">.</span><span class="text-ink">voto</span>
    </span>
    <span class="text-ink-faint text-sm">{t(locale, "results.shareTitle")}</span>
  </div>

  <!-- Affinity summary -->
  <p class="text-sm text-ink-soft mb-4">
    <span class="font-semibold text-brand">{affinity}%</span>
    {t(locale, "quiz.affinity")}
    {locale === "pt-BR" ? "com" : "con"}
    <span class="font-semibold">{topCandidate}</span>
  </p>

  <!-- Share buttons -->
  <div class="flex flex-wrap gap-3">
    <a
      href={whatsappUrl}
      target="_blank"
      rel="noopener noreferrer"
      class="flex items-center gap-2.5 px-4 py-2.5 bg-[#25D366]/10 text-[#25D366] rounded-lg text-sm font-medium hover:bg-[#25D366]/20 transition-colors"
      aria-label="Compartir en WhatsApp"
      onclick={() => { if (typeof window !== "undefined" && (window as any).__pvEvent) (window as any).__pvEvent("result_shared", { method: "whatsapp" }); }}
    >
      <MessageCircle size={20} />
      <span>WhatsApp</span>
    </a>
    <a
      href={twitterUrl}
      target="_blank"
      rel="noopener noreferrer"
      class="flex items-center gap-2.5 px-4 py-2.5 bg-ink/5 text-ink-soft rounded-lg text-sm font-medium hover:bg-ink/10 transition-colors"
      aria-label="Compartir en X"
      onclick={() => { if (typeof window !== "undefined" && (window as any).__pvEvent) (window as any).__pvEvent("result_shared", { method: "x" }); }}
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
      <span>X</span>
    </a>
    <a
      href={telegramUrl}
      target="_blank"
      rel="noopener noreferrer"
      class="flex items-center gap-2.5 px-4 py-2.5 bg-[#0088cc]/10 text-[#0088cc] rounded-lg text-sm font-medium hover:bg-[#0088cc]/20 transition-colors"
      aria-label="Compartir en Telegram"
      onclick={() => { if (typeof window !== "undefined" && (window as any).__pvEvent) (window as any).__pvEvent("result_shared", { method: "telegram" }); }}
    >
      <Send size={20} />
      <span>Telegram</span>
    </a>
    <button
      onclick={copyLink}
      class="flex items-center gap-2.5 px-4 py-2.5 bg-paper-warm text-ink-soft rounded-lg text-sm font-medium hover:bg-line transition-colors"
      aria-label={t(locale, "common.copyLink")}
    >
      <Link size={20} />
      <span>{copied ? t(locale, "common.copied") : t(locale, "common.copyLink")}</span>
    </button>
  </div>
</div>
