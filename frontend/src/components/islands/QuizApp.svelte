<script lang="ts">
  import { t, type Locale } from "../../lib/i18n";
  import { computeAffinity } from "../../lib/quiz";
  import ResultsShare from "./ResultsShare.svelte";
  import { ChevronDown, ChevronUp } from "lucide-svelte";
  import type {
    StatementOut,
    CandidateOut,
    CandidateDetail,
    CandidateAffinity,
    PositionOut,
  } from "../../lib/types";

  interface Props {
    country: string;
    locale?: Locale;
  }

  let { country, locale = "es" }: Props = $props();

  type Screen = "welcome" | "quiz" | "results" | "shared";

  let screen = $state<Screen>("welcome");
  let currentIndex = $state(0);
  let answers = $state<Map<string, number | null>>(new Map());
  let statements = $state<StatementOut[]>([]);
  let candidates = $state<CandidateOut[]>([]);
  let candidatePositions = $state<Map<string, PositionOut[]>>(new Map());
  let results = $state<CandidateAffinity[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let showBreakdown = $state(false);

  // Shared result state (populated from hash fragment)
  let sharedCandidate = $state<CandidateOut | null>(null);
  let sharedPct = $state<number>(0);
  let sharedHc = $state<number | null>(null);

  function hcBadgeColor(pct: number | null): string {
    if (pct === null || pct < 30) return "var(--color-ink-faint)";
    if (pct >= 60) return "#16a34a";
    return "#d97706";
  }
  const sharedColor = $derived(sharedCandidate?.color || "#737373");
  const sharedInitials = $derived(
    sharedCandidate
      ? sharedCandidate.name.split(" ").map((w: string) => w[0]).slice(0, 2).join("").toUpperCase()
      : ""
  );

  const STORAGE_KEY = $derived(`prevoto-quiz-${country}`);
  const baseUrl = "/api";
  let quizStartTime = $state<number>(0);

  function trackEvent(eventType: string, params: Record<string, unknown> = {}) {
    const payload: Record<string, unknown> = { event_type: eventType, country: country, ...params };
    fetch(`${baseUrl}/usage/event`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).catch(() => {});
    if (typeof window !== "undefined" && (window as any).__pvEvent) {
      (window as any).__pvEvent(eventType, params);
    }
  }

  const answerOptions = [
    { value: 2, key: "quiz.stronglyAgree" },
    { value: 1, key: "quiz.agree" },
    { value: 0, key: "quiz.neutral" },
    { value: -1, key: "quiz.disagree" },
    { value: -2, key: "quiz.stronglyDisagree" },
  ];

  // Load data on mount
  $effect(() => {
    loadData();
  });

  // Keyboard navigation
  $effect(() => {
    if (screen !== "quiz") return;

    function handleKeydown(e: KeyboardEvent) {
      if (e.key >= "1" && e.key <= "5") {
        e.preventDefault();
        const idx = parseInt(e.key) - 1;
        selectAnswer(answerOptions[idx].value);
      } else if (e.key === "ArrowLeft" && currentIndex > 0) {
        e.preventDefault();
        currentIndex--;
      }
    }

    window.addEventListener("keydown", handleKeydown);
    return () => window.removeEventListener("keydown", handleKeydown);
  });

  async function loadData() {
    loading = true;
    error = null;
    try {
      const [stmtRes, candRes] = await Promise.all([
        fetch(`${baseUrl}/quiz/${country}/statements`),
        fetch(`${baseUrl}/candidates/${country}`),
      ]);

      if (!stmtRes.ok || !candRes.ok) {
        error = t(locale, "common.error");
        loading = false;
        return;
      }

      statements = await stmtRes.json();
      candidates = await candRes.json();

      // Fetch positions for each candidate in parallel
      const positionPromises = candidates.map(async (c) => {
        try {
          const res = await fetch(
            `${baseUrl}/candidates/${country}/${c.slug}`
          );
          if (res.ok) {
            const detail: CandidateDetail = await res.json();
            return { slug: c.slug, positions: detail.positions };
          }
        } catch {}
        return { slug: c.slug, positions: [] as PositionOut[] };
      });

      const posResults = await Promise.all(positionPromises);
      const posMap = new Map<string, PositionOut[]>();
      for (const { slug, positions } of posResults) {
        posMap.set(slug, positions);
      }
      candidatePositions = posMap;

      // Check for shared result in hash fragment (e.g. #top=slug&pct=82)
      if (typeof window !== "undefined" && window.location.hash) {
        const hashParams = new URLSearchParams(window.location.hash.slice(1));
        const topSlug = hashParams.get("top");
        const pctStr = hashParams.get("pct");
        if (topSlug && pctStr) {
          const matched = candidates.find((c) => c.slug === topSlug);
          if (matched) {
            sharedCandidate = matched;
            sharedPct = parseInt(pctStr, 10) || 0;
            sharedHc = hashParams.get("hc") ? parseFloat(hashParams.get("hc")!) : null;
            screen = "shared";
            // Clean hash from URL without triggering navigation
            history.replaceState(null, "", window.location.pathname);
            loading = false;
            return;
          }
        }
      }

      // Restore session
      restoreSession();
      loading = false;
    } catch {
      error = t(locale, "common.error");
      loading = false;
    }
  }

  function saveSession() {
    try {
      const data = {
        currentIndex,
        answers: Array.from(answers.entries()),
        screen,
      };
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch {}
  }

  function restoreSession() {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const data = JSON.parse(raw);
      if (data.answers) {
        answers = new Map(data.answers);
      }
      if (typeof data.currentIndex === "number") {
        currentIndex = data.currentIndex;
      }
      if (data.screen === "quiz" || data.screen === "results") {
        screen = data.screen;
      }
      if (data.screen === "results") {
        computeResults();
      }
    } catch {}
  }

  function selectAnswer(value: number) {
    const stmt = statements[currentIndex];
    if (!stmt) return;

    // Fire quiz_started on first answer
    if (answers.size === 0) {
      quizStartTime = Date.now();
      trackEvent("quiz_started");
    }

    // Track answer
    trackEvent("question_answered", {
      statement_id: stmt.id,
      position_value: value,
    });

    answers.set(stmt.id, value);
    answers = new Map(answers); // trigger reactivity

    if (currentIndex < statements.length - 1) {
      currentIndex++;
      saveSession();
      // Track next question view
      const nextStmt = statements[currentIndex];
      if (nextStmt) {
        trackEvent("question_viewed", { statement_id: nextStmt.id });
      }
    } else {
      // Last question
      screen = "results";
      saveSession();
      computeResults();
      submitToServer();

      const duration = quizStartTime > 0 ? Math.round((Date.now() - quizStartTime) / 1000) : undefined;
      trackEvent("quiz_completed", {
        statements_answered: answers.size,
        top_match_slug: results[0]?.slug,
        top_match_pct: results[0] ? Math.round(results[0].affinity * 10) / 10 : undefined,
        duration_seconds: duration,
      });
    }
  }

  function computeResults() {
    const statementWeights: Record<string, number> = {};
    for (const s of statements) {
      statementWeights[s.id] = s.weight;
    }

    const userAnswers: Record<string, number | null> = {};
    for (const [k, v] of answers) {
      userAnswers[k] = v;
    }

    const affinities: CandidateAffinity[] = candidates
      .filter((c) => !c.withdrawn)
      .map((c) => {
        const positions = candidatePositions.get(c.slug) || [];
        const candPositions: Record<string, number> = {};
        const highConfPositions: Record<string, number> = {};
        for (const p of positions) {
          candPositions[p.statement_id] = p.value;
          if (p.confidence === "high") {
            highConfPositions[p.statement_id] = p.value;
          }
        }
        const affinity = computeAffinity(userAnswers, candPositions, statementWeights);
        const affinityHc = Object.keys(highConfPositions).length > 0
          ? computeAffinity(userAnswers, highConfPositions, statementWeights)
          : null;
        return {
          candidate_id: c.id,
          slug: c.slug,
          name: c.name,
          party: c.party,
          party_acronym: c.party_acronym,
          coalition: c.coalition,
          photo_url: c.photo_url,
          color: c.color,
          affinity,
          affinity_high_confidence: affinityHc,
          high_confidence_pct: c.high_confidence_pct,
          running_mate: c.running_mate,
          ballot_position: c.ballot_position,
        };
      });

    affinities.sort((a, b) => b.affinity - a.affinity);
    results = affinities;
  }

  async function submitToServer() {
    try {
      const answersObj: Record<string, number | null> = {};
      for (const [k, v] of answers) {
        answersObj[k] = v;
      }
      const res = await fetch(`${baseUrl}/quiz/${country}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers: answersObj }),
      });
      if (res.ok) {
        const serverResult = await res.json();
        if (serverResult.results) {
          results = serverResult.results;
        }
      } else if (res.status === 423) {
        // Veda: quiz is temporarily disabled
        window.location.replace(`/${country}/veda`);
      }
    } catch {
      // Keep optimistic results
    }
  }

  function restart() {
    sessionStorage.removeItem(STORAGE_KEY);
    answers = new Map();
    currentIndex = 0;
    results = [];
    showBreakdown = false;
    screen = "welcome";
  }

  function goBack() {
    if (currentIndex > 0) {
      currentIndex--;
    } else {
      screen = "welcome";
    }
    saveSession();
  }

  function getPositionLabel(value: number): string {
    return t(locale, `position.${value}`);
  }

  const currentStatement = $derived(statements[currentIndex]);
  const progressPct = $derived(
    statements.length > 0
      ? ((currentIndex + (answers.has(currentStatement?.id ?? "") ? 1 : 0)) / statements.length) * 100
      : 0
  );
  const topResult = $derived(results[0]);
  const shareUrl = $derived(
    topResult && typeof window !== "undefined"
      ? `${window.location.origin}/${country}/quiz?top=${topResult.slug}&pct=${Math.round(topResult.affinity)}${topResult.affinity_high_confidence !== null ? `&hc=${Math.round(topResult.affinity_high_confidence * 10) / 10}` : ''}&v=1`
      : `https://pre.voto/${country}/quiz`
  );
</script>

<div class="max-w-2xl mx-auto px-4 py-8">
  {#if loading}
    <div class="text-center py-20">
      <p class="text-ink-faint">{t(locale, "common.loading")}</p>
    </div>

  {:else if error}
    <div class="text-center py-20">
      <p class="text-brand">{error}</p>
    </div>

  {:else if screen === "welcome"}
    <!-- Welcome screen -->
    <div class="text-center py-8">
      <h1 class="text-3xl font-bold mb-3">{t(locale, "quiz.title")}</h1>
      <div class="text-lg text-ink-soft mb-6 space-y-3 max-w-lg mx-auto text-left">
        <p>{t(locale, "quiz.welcomeP1")}</p>
        <p>{t(locale, "quiz.welcomeP2")}</p>
        <p>{t(locale, "quiz.welcomeP3")}</p>
      </div>

      <div class="flex justify-center gap-4 mb-8 text-sm text-ink-faint">
        <span class="bg-paper-warm px-3 py-1 rounded-full">{t(locale, "quiz.time")}</span>
        <span class="bg-paper-warm px-3 py-1 rounded-full">{t(locale, "quiz.noRegistration")}</span>
        <span class="bg-paper-warm px-3 py-1 rounded-full">{t(locale, "quiz.localProcessing")}</span>
      </div>

      <!-- Bloque A: Ley 2494 disclaimer -->
      <div class="mt-8 max-w-lg mx-auto text-left">
        <aside class="bg-ocre/5 border border-ocre/30 rounded-lg px-6 py-5">
          <p class="text-sm leading-relaxed text-ink-soft">
            {t(locale, "disclaimer.ley2494Quiz")}
          </p>
        </aside>
      </div>

      <!-- Bloque B: Withdrawn candidates -->
      <div class="mt-4 max-w-lg mx-auto text-left">
        <aside class="bg-paper-warm border border-steel/20 rounded-lg px-6 py-5">
          <p class="text-sm font-semibold text-ink mb-1">
            {t(locale, "disclaimer.withdrawnTitle")}
          </p>
          <p class="text-sm leading-relaxed text-ink-soft">
            {t(locale, "disclaimer.withdrawnCandidates")}
          </p>
        </aside>
      </div>

      <button
        onclick={() => { screen = "quiz"; saveSession(); if (statements[0]) trackEvent("question_viewed", { statement_id: statements[0].id }); }}
        class="mt-8 px-8 py-3 bg-brand text-white rounded-lg font-medium text-lg hover:bg-brand-dark transition-colors"
      >
        {t(locale, "quiz.start")}
      </button>

      <div class="mt-6 max-w-md mx-auto">
        <aside class="text-xs text-ink-faint text-left leading-relaxed">
          <p>{t(locale, "disclaimer.quiz")}</p>
        </aside>
      </div>
    </div>

  {:else if screen === "quiz" && currentStatement}
    <!-- Quiz screen -->
    <div>
      <!-- Progress -->
      <div class="mb-6">
        <div class="flex justify-between text-sm text-ink-faint mb-2">
          <span>{t(locale, "quiz.questionOf", { current: currentIndex + 1, total: statements.length })}</span>
          {#if currentStatement.category}
            <span class="text-ink-soft">{currentStatement.category}</span>
          {/if}
        </div>
        <div class="h-1.5 bg-paper-warm rounded-full overflow-hidden">
          <div
            class="h-full bg-brand rounded-full transition-all duration-300"
            style="width: {progressPct}%"
          ></div>
        </div>
      </div>

      <!-- Statement -->
      <div class="py-8 text-center" aria-live="polite">
        <p class="text-xl md:text-2xl font-medium leading-relaxed">
          {currentStatement.text}
        </p>
      </div>

      <!-- Answer buttons -->
      <div class="space-y-2 mb-6">
        {#each answerOptions as opt}
          {@const isSelected = answers.get(currentStatement.id) === opt.value}
          <button
            onclick={() => selectAnswer(opt.value)}
            class="w-full py-3 px-4 rounded-lg border text-left transition-all {isSelected
              ? 'border-brand bg-brand/10 text-brand font-medium'
              : 'border-line hover:border-ink-faint'}"
          >
            {t(locale, opt.key)}
          </button>
        {/each}
      </div>

      <!-- Back button -->
      <button
        onclick={goBack}
        class="text-sm text-ink-faint hover:text-ink"
      >
        &larr; {t(locale, "quiz.back")}
      </button>

      <!-- Keyboard hint (desktop only) -->
      <p class="hidden md:block text-xs text-ink-faint text-center mt-4">
        {locale === "pt-BR"
          ? "Teclas 1-5 para responder, setas para navegar"
          : "Teclas 1-5 para responder, flechas para navegar"}
      </p>

      <!-- Methodology link -->
      <p class="text-xs text-ink-faint text-center mt-3">
        <a href="/metodologia" target="_blank" rel="noopener noreferrer" class="hover:text-brand hover:underline">
          {t(locale, "quiz.howCalculated")}
        </a>
      </p>
    </div>

  {:else if screen === "shared" && sharedCandidate}
    <!-- Shared result screen -->
    {@const sharedIsLowConf = (sharedCandidate.high_confidence_pct ?? 100) < 30}
    {@const sharedIsZeroConf = sharedCandidate.high_confidence_pct === 0}
    <div class="text-center py-8">
      <h2 class="text-2xl font-bold mb-6">{t(locale, "shared.title")}</h2>

      <div
        class="border border-line rounded-lg p-6 mb-8 max-w-md mx-auto"
        style={sharedIsLowConf ? "border-left: 3px solid var(--color-ink-faint)" : ""}
      >
        <div class="flex flex-col items-center gap-3">
          {#if sharedCandidate.photo_url}
            <img
              src={sharedCandidate.photo_url}
              alt={sharedCandidate.name}
              width="64"
              height="64"
              class="w-16 h-16 rounded-full object-cover"
            />
          {:else}
            <div
              class="w-16 h-16 rounded-full flex items-center justify-center text-white text-lg font-bold"
              style="background-color: {sharedColor}"
            >
              {sharedInitials}
            </div>
          {/if}
          <p class="text-4xl font-bold" style="color: {sharedColor}">{sharedPct}%</p>
          <p class="text-lg font-medium">{sharedCandidate.name}</p>
          {#if sharedCandidate.coalition || sharedCandidate.party_acronym || sharedCandidate.party}
            <p class="text-sm text-ink-faint">
              {sharedCandidate.coalition || sharedCandidate.party_acronym || sharedCandidate.party}
            </p>
          {/if}

          <!-- HC secondary percentage (shared) -->
          {#if sharedHc !== null}
            <p class="text-sm text-ink-faint">
              {t(locale, "results.hcLabel")} {Math.round(sharedHc)}%
            </p>
          {/if}

          <!-- HC badge (shared) -->
          {#if sharedCandidate.high_confidence_pct !== null && sharedCandidate.high_confidence_pct !== undefined}
            <div class="group relative">
              <span class="text-xs font-medium" style="color: {hcBadgeColor(sharedCandidate.high_confidence_pct)}">
                ● {t(locale, "results.hcBadge", { pct: sharedCandidate.high_confidence_pct })}
              </span>
              <span class="hidden md:group-hover:block absolute left-1/2 -translate-x-1/2 top-full mt-1 z-10 bg-ink text-paper text-xs rounded px-3 py-2 max-w-xs leading-relaxed shadow-lg text-left">
                {t(locale, "results.hcTooltip", { count: Math.round((sharedCandidate.high_confidence_pct / 100) * 20) })}
              </span>
            </div>
          {/if}
        </div>

        <!-- Low-conf caption (shared) -->
        {#if sharedIsLowConf && !sharedIsZeroConf}
          <p class="mt-3 text-xs text-ink-faint italic text-left">
            {t(locale, "results.lowConfCaption")}
            <a href="/{country}/candidatos/{sharedCandidate.slug}" class="text-brand hover:underline not-italic">
              {t(locale, "results.lowConfLink")}
            </a>
          </p>
        {/if}

        <!-- Zero-conf warning (shared) -->
        {#if sharedIsZeroConf}
          <aside class="mt-3 bg-paper-warm border border-line rounded-lg px-4 py-3 text-left">
            <p class="text-xs leading-relaxed text-ink-soft">
              {t(locale, "results.zeroConfWarning", { name: sharedCandidate.name })}
            </p>
          </aside>
        {/if}
      </div>

      <p class="text-ink-soft mb-6">{t(locale, "shared.cta")}</p>
      <button
        onclick={() => { screen = "welcome"; }}
        class="px-8 py-3 bg-brand text-white rounded-lg font-medium text-lg hover:bg-brand-dark transition-colors"
      >
        {t(locale, "country.startQuiz")}
      </button>
    </div>

  {:else if screen === "results" && results.length > 0}
    <!-- Results screen -->
    <div>
      <h2 class="text-2xl font-bold mb-6 text-center">{t(locale, "quiz.yourResults")}</h2>

      <div class="space-y-4 mb-8">
        {#each results as result, i}
          {@const color = result.color || "#737373"}
          {@const initials = result.name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase()}
          {@const isLowConf = (result.high_confidence_pct ?? 100) < 30}
          {@const isZeroConf = result.high_confidence_pct === 0}
          <div
            class="border border-line rounded-lg p-4"
            style={isLowConf ? "border-left: 3px solid var(--color-ink-faint)" : ""}
          >
            <div class="flex items-center gap-3 mb-2">
              {#if result.photo_url}
                <img
                  src={result.photo_url}
                  alt={result.name}
                  width="40"
                  height="40"
                  class="w-10 h-10 rounded-full object-cover"
                />
              {:else}
                <div
                  class="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold"
                  style="background-color: {color}"
                >
                  {initials}
                </div>
              {/if}
              <div class="flex-1 min-w-0">
                <div class="flex items-baseline justify-between">
                  <span class="font-medium">{result.name}</span>
                  <span class="font-bold text-lg" style="color: {color}">
                    {result.affinity}%
                  </span>
                </div>
                {#if result.coalition || result.party_acronym || result.party}
                  <span class="text-sm text-ink-faint">
                    {result.coalition || result.party_acronym || result.party}
                  </span>
                {/if}
              </div>
            </div>
            <div class="h-2 bg-paper-warm rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-700"
                style="width: {result.affinity}%; background-color: {color}"
              ></div>
            </div>

            <!-- HC secondary percentage -->
            <div class="mt-2 text-sm text-ink-faint">
              {#if result.affinity_high_confidence !== null}
                <span>{t(locale, "results.hcLabel")} {Math.round(result.affinity_high_confidence)}%</span>
              {:else}
                <span class="italic">{t(locale, "results.hcNone")}</span>
              {/if}
            </div>

            <!-- HC badge -->
            {#if result.high_confidence_pct !== null && result.high_confidence_pct !== undefined}
              <div class="mt-1 group relative">
                <span class="text-xs font-medium" style="color: {hcBadgeColor(result.high_confidence_pct)}">
                  ● {t(locale, "results.hcBadge", { pct: result.high_confidence_pct })}
                </span>
                <span class="hidden md:group-hover:block absolute left-0 top-full mt-1 z-10 bg-ink text-paper text-xs rounded px-3 py-2 max-w-xs leading-relaxed shadow-lg">
                  {t(locale, "results.hcTooltip", { count: Math.round((result.high_confidence_pct / 100) * 20) })}
                </span>
              </div>
            {/if}

            <!-- Low-conf caption -->
            {#if isLowConf && !isZeroConf}
              <p class="mt-2 text-xs text-ink-faint italic">
                {t(locale, "results.lowConfCaption")}
                <a href="/{country}/candidatos/{result.slug}" class="text-brand hover:underline not-italic">
                  {t(locale, "results.lowConfLink")}
                </a>
              </p>
            {/if}

            <!-- Zero-conf warning -->
            {#if isZeroConf}
              <aside class="mt-3 bg-paper-warm border border-line rounded-lg px-4 py-3">
                <p class="text-xs leading-relaxed text-ink-soft">
                  {t(locale, "results.zeroConfWarning", { name: result.name })}
                </p>
              </aside>
            {/if}
          </div>
        {/each}
      </div>

      <!-- Bloque C: Results interpretation disclaimer -->
      <aside class="bg-ocre/5 border border-ocre/30 rounded-lg px-6 py-5 mb-8">
        <p class="text-sm font-semibold text-ink mb-1">
          {t(locale, "disclaimer.resultsTitle")}
        </p>
        <p class="text-sm leading-relaxed text-ink-soft">
          {t(locale, "disclaimer.resultsInterpretation")}
        </p>
      </aside>

      <!-- Statement breakdown -->
      <div class="mb-8">
        <button
          onclick={() => showBreakdown = !showBreakdown}
          class="text-sm text-brand hover:text-brand-dark font-medium inline-flex items-center gap-1"
        >
          {#if showBreakdown}<ChevronUp size={16} />{:else}<ChevronDown size={16} />{/if}
          {t(locale, "quiz.statementBreakdown")}
        </button>

        {#if showBreakdown}
          <div class="mt-4 space-y-4">
            {#each statements as stmt}
              {@const userAnswer = answers.get(stmt.id)}
              <div class="border border-line rounded-lg p-4">
                <p class="font-medium mb-3">{stmt.text}</p>
                {#if userAnswer !== undefined && userAnswer !== null}
                  <p class="text-sm mb-2">
                    <span class="text-ink-faint">{t(locale, "quiz.yourAnswer")}:</span>
                    <span class="font-medium"> {getPositionLabel(userAnswer)}</span>
                  </p>
                {/if}
                <div class="space-y-1">
                  {#each results as result}
                    {@const positions = candidatePositions.get(result.slug) || []}
                    {@const pos = positions.find((p) => p.statement_id === stmt.id)}
                    <div class="flex items-center gap-2 text-sm">
                      <span
                        class="w-2 h-2 rounded-full flex-shrink-0"
                        style="background-color: {result.color || '#737373'}"
                      ></span>
                      <span class="text-ink-soft w-32 flex-shrink-0 truncate">{result.name}</span>
                      {#if pos}
                        <span>{getPositionLabel(pos.value)}</span>
                        {#if pos.source_url}
                          <a
                            href={pos.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            class="text-brand text-xs hover:underline ml-auto"
                          >
                            {t(locale, "common.source")}
                          </a>
                        {/if}
                      {:else}
                        <span class="text-ink-faint italic">{t(locale, "quiz.noPosition")}</span>
                      {/if}
                    </div>
                  {/each}
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Share -->
      {#if topResult}
        <ResultsShare
          url={shareUrl}
          topCandidate={topResult.name}
          topSlug={topResult.slug}
          affinity={topResult.affinity}
          {country}
          {locale}
        />
      {/if}

      <!-- Restart -->
      <div class="text-center mt-6">
        <button
          onclick={restart}
          class="text-sm text-ink-faint hover:text-ink underline"
        >
          {t(locale, "quiz.restart")}
        </button>
      </div>
    </div>
  {/if}
</div>
