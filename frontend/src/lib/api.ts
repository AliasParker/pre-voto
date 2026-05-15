import type {
  CountryOut,
  CountryDetail,
  CandidateOut,
  CandidateDetail,
  StatementOut,
  QuizResult,
  ArticleOut,
  ArticleDetail,
  PollOut,
  PollAverageOut,
  SubscriberOut,
} from "./types";

function getBaseUrl(): string {
  if (import.meta.env.SSR) {
    return import.meta.env.API_INTERNAL_URL || "http://api:8000";
  }
  return "/api";
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T | null> {
  try {
    const res = await fetch(`${getBaseUrl()}${path}`, init);
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export async function fetchCountries(): Promise<CountryOut[]> {
  return (await apiFetch<CountryOut[]>("/countries")) ?? [];
}

export async function fetchCountry(code: string): Promise<CountryDetail | null> {
  return apiFetch<CountryDetail>(`/countries/${code}`);
}

export async function fetchStatements(country: string): Promise<StatementOut[]> {
  return (await apiFetch<StatementOut[]>(`/quiz/${country}/statements`)) ?? [];
}

export async function submitQuiz(
  country: string,
  answers: Record<string, number | null>,
): Promise<QuizResult | null> {
  return apiFetch<QuizResult>(`/quiz/${country}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers }),
  });
}

export async function fetchCandidates(country: string): Promise<CandidateOut[]> {
  return (await apiFetch<CandidateOut[]>(`/candidates/${country}`)) ?? [];
}

export async function fetchCandidate(
  country: string,
  slug: string,
): Promise<CandidateDetail | null> {
  return apiFetch<CandidateDetail>(`/candidates/${country}/${slug}`);
}

export async function fetchArticles(
  country: string,
  offset = 0,
  limit = 20,
): Promise<ArticleOut[]> {
  return (
    (await apiFetch<ArticleOut[]>(
      `/articles/${country}?offset=${offset}&limit=${limit}`,
    )) ?? []
  );
}

export async function fetchArticle(
  country: string,
  slug: string,
): Promise<ArticleDetail | null> {
  return apiFetch<ArticleDetail>(`/articles/${country}/${slug}`);
}

export async function fetchPolls(country: string): Promise<PollOut[]> {
  return (await apiFetch<PollOut[]>(`/polls/${country}`)) ?? [];
}

export async function fetchPollAverage(
  country: string,
): Promise<PollAverageOut | null> {
  return apiFetch<PollAverageOut>(`/polls/${country}/average`);
}

export async function subscribeNewsletter(data: {
  email: string;
  country_code?: string;
  source?: string;
}): Promise<SubscriberOut | null> {
  return apiFetch<SubscriberOut>("/subscribers", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}
