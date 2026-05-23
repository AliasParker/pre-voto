<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright (c) 2026 Equipo pre.voto -->
<script>
  let status = $state("loading...");

  $effect(() => {
    status = "svelte ok";
  });
</script>

<p class="mt-4 text-sm text-ink-faint" data-testid="svelte-health">{status}</p>
