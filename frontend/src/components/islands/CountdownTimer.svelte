<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright (c) 2026 Equipo pre.voto -->
<script lang="ts">
  import { t, type Locale } from "../../lib/i18n";

  interface Props {
    targetDate: string;
    locale?: Locale;
  }

  let { targetDate, locale = "es" }: Props = $props();

  let now = $state(Date.now());
  let interval: ReturnType<typeof setInterval> | undefined;

  const target = $derived(new Date(targetDate).getTime());

  $effect(() => {
    interval = setInterval(() => {
      now = Date.now();
    }, 1000);

    return () => {
      if (interval) clearInterval(interval);
    };
  });

  const diff = $derived(target - now);
  const isPast = $derived(diff <= 0);
  const isToday = $derived(diff > 0 && diff < 86400000);

  const days = $derived(Math.floor(diff / 86400000));
  const hours = $derived(Math.floor((diff % 86400000) / 3600000));
  const minutes = $derived(Math.floor((diff % 3600000) / 60000));
  const seconds = $derived(Math.floor((diff % 60000) / 1000));
</script>

{#if isPast}
  <p class="text-ink-soft font-medium">{t(locale, "common.electionEnded")}</p>
{:else if isToday}
  <p class="text-brand font-bold text-lg">{t(locale, "common.electionDay")}</p>
{:else}
  <div class="flex gap-4 text-center">
    <div>
      <span class="text-2xl md:text-3xl font-bold tabular-nums">{days}</span>
      <span class="block text-xs text-ink-faint">{t(locale, "common.days")}</span>
    </div>
    <div>
      <span class="text-2xl md:text-3xl font-bold tabular-nums">{hours}</span>
      <span class="block text-xs text-ink-faint">{t(locale, "common.hours")}</span>
    </div>
    <div>
      <span class="text-2xl md:text-3xl font-bold tabular-nums">{String(minutes).padStart(2, "0")}</span>
      <span class="block text-xs text-ink-faint">{t(locale, "common.mins")}</span>
    </div>
    <div>
      <span class="text-2xl md:text-3xl font-bold tabular-nums">{String(seconds).padStart(2, "0")}</span>
      <span class="block text-xs text-ink-faint">{t(locale, "common.secs")}</span>
    </div>
  </div>
{/if}
