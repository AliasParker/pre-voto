<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright (c) 2026 Equipo pre.voto -->
<script lang="ts">
  let visible = $state(false);

  $effect(() => {
    if (typeof window === "undefined") return;
    const stored = localStorage.getItem("prevoto_cookie_consent");
    if (!stored) {
      visible = true;
    }
  });

  function accept() {
    localStorage.setItem("prevoto_cookie_consent", "accepted");
    visible = false;
    window.dispatchEvent(
      new CustomEvent("cookie-consent-changed", { detail: { consent: "accepted" } })
    );
  }

  function reject() {
    localStorage.setItem("prevoto_cookie_consent", "rejected");
    visible = false;
    window.dispatchEvent(
      new CustomEvent("cookie-consent-changed", { detail: { consent: "rejected" } })
    );
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Escape") {
      // Escape dismisses visually but doesn't set preference — banner returns next visit
      visible = false;
    }
  }
</script>

{#if visible}
  <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
  <div
    role="region"
    aria-label="Consentimiento de cookies"
    class="fixed bottom-0 left-0 right-0 z-50 border-t border-line bg-paper px-4 py-4 shadow-lg"
    onkeydown={handleKeydown}
  >
    <div class="max-w-3xl mx-auto flex flex-col sm:flex-row items-start sm:items-center gap-3">
      <p class="text-sm text-ink-soft flex-1">
        Pre.voto usa cookies de Google Analytics para entender qué páginas son más útiles.
        No vendemos datos ni mostramos publicidad.
        Puedes rechazar y el sitio funciona igual.
      </p>
      <div class="flex items-center gap-2 flex-shrink-0">
        <button
          onclick={accept}
          class="px-4 py-2 text-sm font-medium rounded-lg border border-line bg-paper-warm text-ink hover:bg-line transition-colors"
        >
          Aceptar
        </button>
        <button
          onclick={reject}
          class="px-4 py-2 text-sm font-medium rounded-lg border border-line bg-paper-warm text-ink hover:bg-line transition-colors"
        >
          Rechazar
        </button>
        <a
          href="/privacidad"
          class="px-4 py-2 text-sm font-medium rounded-lg border border-line bg-paper-warm text-ink hover:bg-line transition-colors"
        >
          Más info
        </a>
      </div>
    </div>
  </div>
{/if}
