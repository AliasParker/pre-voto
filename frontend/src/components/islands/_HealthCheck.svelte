<script>
  let status = $state("loading...");

  $effect(() => {
    status = "svelte ok";
  });
</script>

<p class="mt-4 text-sm text-ink-faint" data-testid="svelte-health">{status}</p>
