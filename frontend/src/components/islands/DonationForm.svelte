<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright (c) 2026 Equipo pre.voto -->
<script lang="ts">
  import { t, type Locale } from "../../lib/i18n";

  export let locale: Locale = "es";

  const presetAmounts = [5, 10, 25];
  const TIMEOUT_MS = 10_000;

  let customAmount: string = "";
  let showCustom: boolean = false;
  let loadingAmount: number | null = null;
  let error: string = "";
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  function toggleCustom() {
    showCustom = !showCustom;
    if (!showCustom) {
      customAmount = "";
      error = "";
    }
  }

  function getCustomAmount(): number {
    const parsed = parseFloat(customAmount);
    return isNaN(parsed) ? 0 : parsed;
  }

  function clearTimer() {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  }

  function resetLoading() {
    loadingAmount = null;
    clearTimer();
  }

  async function donate(amount: number) {
    error = "";
    if (amount < 1) {
      error = t(locale, "donate.errorMinAmount");
      return;
    }

    loadingAmount = amount;

    // 10s timeout fallback
    timeoutId = setTimeout(() => {
      error = t(locale, "donate.errorTimeout");
      resetLoading();
    }, TIMEOUT_MS);

    try {
      const res = await fetch("/api/donations/create-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount_usd: amount }),
      });

      clearTimer();

      if (!res.ok) {
        const data = await res.json().catch(() => null);
        error = data?.error?.message || t(locale, "donate.errorGeneric");
        loadingAmount = null;
        return;
      }

      const data = await res.json();
      if (data.checkout_url) {
        // Keep loading state while redirecting
        window.location.href = data.checkout_url;
      } else {
        loadingAmount = null;
      }
    } catch {
      clearTimer();
      error = t(locale, "donate.errorGeneric");
      loadingAmount = null;
    }
  }

  function handlePreset(amount: number) {
    donate(amount);
  }

  function handleCustomSubmit() {
    const amount = getCustomAmount();
    donate(amount);
  }
</script>

<div
  class="max-w-md mx-auto space-y-6"
  class:cursor-wait={loadingAmount !== null}
>
  <!-- Preset amount buttons -->
  <div class="flex gap-4 justify-center">
    {#each presetAmounts as amount}
      <button
        type="button"
        disabled={loadingAmount !== null}
        class="flex-1 py-5 px-6 rounded-xl border-2 font-bold text-xl
          transition-all duration-200 min-h-[60px]
          {loadingAmount === amount
          ? 'border-terracotta bg-terracotta text-white cursor-wait scale-[0.97]'
          : loadingAmount !== null
            ? 'border-line bg-paper-warm text-ink opacity-40 cursor-not-allowed'
            : 'border-line bg-paper-warm text-ink hover:border-terracotta hover:shadow-md active:scale-95'}"
        on:click={() => handlePreset(amount)}
      >
        {#if loadingAmount === amount}
          <span class="inline-flex items-center justify-center gap-2">
            <svg class="animate-spin h-5 w-5 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <span class="text-base">{t(locale, "donate.processing")}</span>
          </span>
        {:else}
          ${amount}
        {/if}
      </button>
    {/each}
  </div>

  <!-- Collapsible custom amount -->
  <div class="text-center">
    <button
      type="button"
      disabled={loadingAmount !== null}
      class="text-sm transition-colors
        {loadingAmount !== null
        ? 'text-ink-soft/40 cursor-not-allowed'
        : 'text-terracotta hover:underline'}"
      on:click={toggleCustom}
    >
      {showCustom ? t(locale, "donate.hideCustom") : t(locale, "donate.showCustom")}
    </button>
  </div>

  {#if showCustom}
    <div class="flex gap-3 items-end">
      <div class="flex-1 relative">
        <span
          class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-soft font-bold"
          >$</span
        >
        <input
          type="number"
          min="1"
          max="10000"
          step="1"
          disabled={loadingAmount !== null}
          bind:value={customAmount}
          placeholder="50"
          class="w-full pl-8 pr-16 py-3 rounded-lg border border-line bg-white
            dark:bg-gray-800 text-ink text-lg focus:border-terracotta focus:outline-none
            disabled:opacity-40 disabled:cursor-not-allowed"
        />
        <span
          class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-soft text-sm"
          >USD</span
        >
      </div>
      <button
        type="button"
        disabled={loadingAmount !== null}
        class="py-3 px-6 rounded-lg font-bold text-white transition-all duration-200
          min-w-[120px] min-h-[48px]
          {loadingAmount !== null && loadingAmount === getCustomAmount()
          ? 'bg-terracotta cursor-wait'
          : loadingAmount !== null
            ? 'bg-gray-400 opacity-40 cursor-not-allowed'
            : 'bg-terracotta hover:bg-terracotta/90 active:scale-95'}"
        on:click={handleCustomSubmit}
      >
        {#if loadingAmount !== null && loadingAmount === getCustomAmount()}
          <span class="inline-flex items-center justify-center gap-2">
            <svg class="animate-spin h-5 w-5 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <span class="text-sm">{t(locale, "donate.processing")}</span>
          </span>
        {:else}
          {t(locale, "donate.submit")}
        {/if}
      </button>
    </div>
  {/if}

  <!-- Error -->
  {#if error}
    <p class="text-red-600 dark:text-red-400 text-sm text-center leading-relaxed">
      {error}
    </p>
  {/if}
</div>
