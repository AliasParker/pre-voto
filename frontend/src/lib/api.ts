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
import { countries as countryMeta } from "./countries";

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
  const result = await apiFetch<CountryOut[]>("/countries");
  if (result && result.length > 0) return result;

  // Fallback: if API is unreachable during build, return minimal country
  // objects from hardcoded metadata so getStaticPaths() generates routes.
  // Pages will render with empty data but won't 404.
  if (import.meta.env.SSR) {
    console.warn(
      "[api] fetchCountries failed — using fallback country list for route generation",
    );
    return Object.entries(countryMeta)
      .filter(([, meta]) => meta.active)
      .map(([code, meta]) => ({
        id: code,
        code,
        name: meta.name.es,
        language: meta.locale === "pt-BR" ? "pt" : meta.locale,
        is_active: meta.active,
        next_election: null,
      }));
  }

  return [];
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

export async function fetchArticlesPreview(
  country: string,
  token: string,
  offset = 0,
  limit = 100,
): Promise<ArticleOut[]> {
  return (
    (await apiFetch<ArticleOut[]>(
      `/articles/${country}/preview?token=${encodeURIComponent(token)}&offset=${offset}&limit=${limit}`,
    )) ?? []
  );
}

export async function fetchArticlePreview(
  country: string,
  slug: string,
  token: string,
): Promise<ArticleDetail | null> {
  return apiFetch<ArticleDetail>(
    `/articles/${country}/preview/${slug}?token=${encodeURIComponent(token)}`,
  );
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
