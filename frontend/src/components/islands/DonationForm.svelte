<script lang="ts">
  import { t, type Locale } from "../../lib/i18n";

  export let locale: Locale = "es";

  const presetAmounts = [5, 10, 25];

  let selectedAmount: number | null = null;
  let customAmount: string = "";
  let email: string = "";
  let newsletterOptIn: boolean = false;
  let loading: boolean = false;
  let error: string = "";

  function selectPreset(amount: number) {
    selectedAmount = amount;
    customAmount = "";
    error = "";
  }

  function handleCustomInput() {
    selectedAmount = null;
    error = "";
  }

  function getAmount(): number {
    if (selectedAmount !== null) return selectedAmount;
    const parsed = parseFloat(customAmount);
    return isNaN(parsed) ? 0 : parsed;
  }

  function isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  async function handleSubmit() {
    error = "";
    const amount = getAmount();

    if (amount < 1) {
      error = t(locale, "donate.errorMinAmount");
      return;
    }
    if (!isValidEmail(email)) {
      error = t(locale, "donate.errorEmail");
      return;
    }

    loading = true;
    try {
      const res = await fetch("/api/donations/create-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amount_usd: amount,
          email,
          newsletter_opt_in: newsletterOptIn,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => null);
        error =
          data?.error?.message || t(locale, "donate.errorGeneric");
        return;
      }

      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch {
      error = t(locale, "donate.errorGeneric");
    } finally {
      loading = false;
    }
  }
</script>

<form
  on:submit|preventDefault={handleSubmit}
  class="max-w-md mx-auto space-y-6"
>
  <!-- Amount presets -->
  <div class="flex gap-3 justify-center">
    {#each presetAmounts as amount}
      <button
        type="button"
        class="px-6 py-3 rounded-lg border-2 font-bold text-lg transition-colors
          {selectedAmount === amount
          ? 'border-terracotta bg-terracotta text-white'
          : 'border-line bg-paper-warm text-ink hover:border-terracotta'}"
        on:click={() => selectPreset(amount)}
      >
        ${amount}
      </button>
    {/each}
  </div>

  <!-- Custom amount -->
  <div>
    <label for="custom-amount" class="block text-sm text-ink-soft mb-1">
      {t(locale, "donate.customAmount")}
    </label>
    <div class="relative">
      <span
        class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-soft font-bold"
        >$</span
      >
      <input
        id="custom-amount"
        type="number"
        min="1"
        max="10000"
        step="1"
        bind:value={customAmount}
        on:input={handleCustomInput}
        placeholder="50"
        class="w-full pl-8 pr-16 py-3 rounded-lg border border-line bg-white
          dark:bg-gray-800 text-ink focus:border-terracotta focus:outline-none"
      />
      <span
        class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-soft text-sm"
        >USD</span
      >
    </div>
  </div>

  <!-- Email -->
  <div>
    <label for="donate-email" class="block text-sm text-ink-soft mb-1">
      {t(locale, "donate.email")}
    </label>
    <input
      id="donate-email"
      type="email"
      bind:value={email}
      placeholder="tu@email.com"
      required
      class="w-full px-4 py-3 rounded-lg border border-line bg-white
        dark:bg-gray-800 text-ink focus:border-terracotta focus:outline-none"
    />
  </div>

  <!-- Newsletter opt-in -->
  <label class="flex items-start gap-3 cursor-pointer">
    <input
      type="checkbox"
      bind:checked={newsletterOptIn}
      class="mt-1 h-4 w-4 rounded border-line text-terracotta
        focus:ring-terracotta"
    />
    <span class="text-sm text-ink-soft">
      {t(locale, "donate.newsletter")}
    </span>
  </label>

  <!-- Error -->
  {#if error}
    <p class="text-red-600 dark:text-red-400 text-sm text-center">{error}</p>
  {/if}

  <!-- Submit -->
  <button
    type="submit"
    disabled={loading}
    class="w-full py-3 rounded-lg font-bold text-white transition-colors
      {loading
      ? 'bg-gray-400 cursor-not-allowed'
      : 'bg-terracotta hover:bg-terracotta/90'}"
  >
    {loading ? t(locale, "donate.submitting") : t(locale, "donate.submit")}
  </button>
</form>
