<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright (c) 2026 Equipo pre.voto -->
<script lang="ts">
  import type { PollOut, CandidateOut } from "../../lib/types";

  interface Props {
    polls: PollOut[];
    candidates: CandidateOut[];
  }

  let { polls, candidates }: Props = $props();

  let tooltip = $state<{
    x: number;
    y: number;
    poll: PollOut;
  } | null>(null);

  // Sort polls by date ascending
  const sortedPolls = $derived(
    [...polls].sort(
      (a, b) => new Date(a.field_end).getTime() - new Date(b.field_end).getTime()
    )
  );

  // Build candidate slug → color/name map
  const candidateMap = $derived(
    new Map(candidates.map((c) => [c.slug, c]))
  );

  // Get all unique candidate slugs that appear in polls
  const activeSlugs = $derived(() => {
    const slugs = new Set<string>();
    for (const p of sortedPolls) {
      for (const key of Object.keys(p.results)) {
        slugs.add(key);
      }
    }
    return Array.from(slugs).filter((s) => candidateMap.has(s));
  });

  // Chart dimensions
  const W = 600;
  const H = 300;
  const PAD = { top: 20, right: 20, bottom: 40, left: 45 };
  const chartW = W - PAD.left - PAD.right;
  const chartH = H - PAD.top - PAD.bottom;

  // X scale (time)
  const xExtent = $derived(() => {
    if (sortedPolls.length === 0) return [Date.now(), Date.now()];
    return [
      new Date(sortedPolls[0].field_end).getTime(),
      new Date(sortedPolls[sortedPolls.length - 1].field_end).getTime(),
    ];
  });

  function xScale(date: string): number {
    const [min, max] = xExtent();
    const t = new Date(date).getTime();
    if (max === min) return chartW / 2;
    return ((t - min) / (max - min)) * chartW;
  }

  // Y scale (percentage, auto-scaled)
  const yExtent = $derived(() => {
    let min = Infinity;
    let max = -Infinity;
    for (const p of sortedPolls) {
      for (const v of Object.values(p.results)) {
        const num = v as number;
        if (num < min) min = num;
        if (num > max) max = num;
      }
    }
    if (min === Infinity) return [0, 100];
    const padding = (max - min) * 0.1 || 5;
    return [Math.max(0, Math.floor(min - padding)), Math.ceil(max + padding)];
  });

  function yScale(value: number): number {
    const [min, max] = yExtent();
    if (max === min) return chartH / 2;
    return chartH - ((value - min) / (max - min)) * chartH;
  }

  // Build path for a candidate
  function buildPath(slug: string): string {
    const points: string[] = [];
    for (const poll of sortedPolls) {
      const val = poll.results[slug];
      if (val !== undefined) {
        const x = PAD.left + xScale(poll.field_end);
        const y = PAD.top + yScale(val as number);
        points.push(`${x},${y}`);
      }
    }
    if (points.length === 0) return "";
    return "M" + points.join("L");
  }

  // Y-axis ticks
  const yTicks = $derived(() => {
    const [min, max] = yExtent();
    const step = Math.max(1, Math.ceil((max - min) / 5));
    const ticks: number[] = [];
    for (let v = min; v <= max; v += step) {
      ticks.push(v);
    }
    return ticks;
  });

  // X-axis labels
  const xLabels = $derived(() => {
    if (sortedPolls.length <= 1) {
      return sortedPolls.map((p) => ({
        date: p.field_end,
        label: formatDate(p.field_end),
      }));
    }
    const step = Math.max(1, Math.floor(sortedPolls.length / 4));
    const labels: { date: string; label: string }[] = [];
    for (let i = 0; i < sortedPolls.length; i += step) {
      labels.push({
        date: sortedPolls[i].field_end,
        label: formatDate(sortedPolls[i].field_end),
      });
    }
    return labels;
  });

  function formatDate(d: string): string {
    const date = new Date(d);
    return date.toLocaleDateString("es-CO", { month: "short", day: "numeric" });
  }

  function handlePointHover(poll: PollOut, event: MouseEvent) {
    const svg = (event.target as SVGElement).closest("svg");
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    tooltip = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
      poll,
    };
  }

  function clearTooltip() {
    tooltip = null;
  }
</script>

<div class="relative">
  <svg
    viewBox="0 0 {W} {H}"
    class="w-full h-auto"
    role="img"
    aria-label="Grafico de encuestas"
    onmouseleave={clearTooltip}
  >
    <!-- Grid lines -->
    {#each yTicks() as tick}
      <line
        x1={PAD.left}
        y1={PAD.top + yScale(tick)}
        x2={W - PAD.right}
        y2={PAD.top + yScale(tick)}
        stroke="var(--color-line)"
        stroke-width="0.5"
      />
      <text
        x={PAD.left - 8}
        y={PAD.top + yScale(tick) + 4}
        text-anchor="end"
        fill="var(--color-ink-faint)"
        font-size="10"
      >
        {tick}%
      </text>
    {/each}

    <!-- X-axis labels -->
    {#each xLabels() as label}
      <text
        x={PAD.left + xScale(label.date)}
        y={H - 8}
        text-anchor="middle"
        fill="var(--color-ink-faint)"
        font-size="10"
      >
        {label.label}
      </text>
    {/each}

    <!-- Lines and points -->
    {#each activeSlugs() as slug}
      {@const c = candidateMap.get(slug)}
      {@const color = c?.color || "#737373"}
      {@const path = buildPath(slug)}

      {#if path}
        <path d={path} fill="none" stroke={color} stroke-width="2" />
      {/if}

      {#each sortedPolls as poll}
        {@const val = poll.results[slug]}
        {#if val !== undefined}
          <circle
            cx={PAD.left + xScale(poll.field_end)}
            cy={PAD.top + yScale(val as number)}
            r="4"
            fill={color}
            stroke="var(--color-paper)"
            stroke-width="1.5"
            class="cursor-pointer"
            onmouseenter={(e) => handlePointHover(poll, e)}
            ontouchstart={(e) => {
              const touch = e.touches[0];
              handlePointHover(poll, touch as unknown as MouseEvent);
            }}
          />
        {/if}
      {/each}
    {/each}
  </svg>

  <!-- Tooltip -->
  {#if tooltip}
    <div
      class="absolute bg-paper border border-line rounded-lg shadow-lg p-3 text-xs pointer-events-none z-10"
      style="left: {Math.min(tooltip.x, W - 160)}px; top: {tooltip.y - 10}px; transform: translateY(-100%)"
    >
      <p class="font-medium mb-1">{tooltip.poll.pollster} — {formatDate(tooltip.poll.field_end)}</p>
      {#each Object.entries(tooltip.poll.results).sort(([, a], [, b]) => (b as number) - (a as number)) as [slug, pct]}
        {@const c = candidateMap.get(slug)}
        <div class="flex items-center gap-1">
          <span
            class="w-2 h-2 rounded-full"
            style="background-color: {c?.color || '#737373'}"
          ></span>
          <span>{c?.name || slug}: {pct}%</span>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Legend -->
  <div class="flex flex-wrap gap-3 mt-3 justify-center">
    {#each activeSlugs() as slug}
      {@const c = candidateMap.get(slug)}
      <div class="flex items-center gap-1 text-sm">
        <span
          class="w-3 h-3 rounded-full"
          style="background-color: {c?.color || '#737373'}"
        ></span>
        <span>{c?.name || slug}</span>
      </div>
    {/each}
  </div>
</div>
