<script lang="ts">
  import { t, type Locale } from "../../lib/i18n";

  export let locale: Locale = "es";

  const presetAmounts = [5, 10, 25];

  let customAmount: string = "";
  let showCustom: boolean = false;
  let loadingAmount: number | null = null;
  let error: string = "";

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

  async function donate(amount: number) {
    error = "";
    if (amount < 1) {
      error = t(locale, "donate.errorMinAmount");
      return;
    }

    loadingAmount = amount;
    try {
      const res = await fetch("/api/donations/create-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount_usd: amount }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => null);
        error = data?.error?.message || t(locale, "donate.errorGeneric");
        return;
      }

      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch {
      error = t(locale, "donate.errorGeneric");
    } finally {
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

<div class="max-w-md mx-auto space-y-6">
  <!-- Preset amount buttons -->
  <div class="flex gap-4 justify-center">
    {#each presetAmounts as amount}
      <button
        type="button"
        disabled={loadingAmount !== null}
        class="flex-1 py-4 px-6 rounded-xl border-2 font-bold text-xl
          transition-all duration-150
          {loadingAmount === amount
          ? 'border-terracotta bg-terracotta/80 text-white cursor-wait'
          : loadingAmount !== null
            ? 'border-line bg-paper-warm text-ink/50 cursor-not-allowed'
            : 'border-line bg-paper-warm text-ink hover:border-terracotta hover:shadow-md active:scale-95'}"
        on:click={() => handlePreset(amount)}
      >
        {#if loadingAmount === amount}
          <span class="inline-flex items-center gap-2">
            <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
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
      class="text-sm text-terracotta hover:underline transition-colors"
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
          bind:value={customAmount}
          placeholder="50"
          class="w-full pl-8 pr-16 py-3 rounded-lg border border-line bg-white
            dark:bg-gray-800 text-ink text-lg focus:border-terracotta focus:outline-none"
        />
        <span
          class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-soft text-sm"
          >USD</span
        >
      </div>
      <button
        type="button"
        disabled={loadingAmount !== null}
        class="py-3 px-6 rounded-lg font-bold text-white transition-colors
          {loadingAmount === getCustomAmount()
          ? 'bg-terracotta/80 cursor-wait'
          : loadingAmount !== null
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-terracotta hover:bg-terracotta/90 active:scale-95'}"
        on:click={handleCustomSubmit}
      >
        {#if loadingAmount !== null && loadingAmount === getCustomAmount()}
          <svg class="animate-spin h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
        {:else}
          {t(locale, "donate.submit")}
        {/if}
      </button>
    </div>
  {/if}

  <!-- Error -->
  {#if error}
    <p class="text-red-600 dark:text-red-400 text-sm text-center">{error}</p>
  {/if}
</div>
