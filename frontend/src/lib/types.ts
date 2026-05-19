// TypeScript types mirroring backend Pydantic schemas

export interface ElectionBrief {
  id: string;
  type: string;
  election_date: string;
  description: string | null;
  is_active: boolean;
}

export interface CountryOut {
  id: string;
  code: string;
  name: string;
  language: string;
  is_active: boolean;
  next_election: ElectionBrief | null;
}

export interface CountryDetail {
  id: string;
  code: string;
  name: string;
  language: string;
  is_active: boolean;
  elections: ElectionBrief[];
}

export interface CandidateOut {
  id: string;
  slug: string;
  name: string;
  party: string | null;
  party_acronym: string | null;
  coalition: string | null;
  bio_short: string | null;
  photo_url: string | null;
  color: string | null;
  ballot_position: number | null;
  running_mate: string | null;
  positioning: string | null;
  high_confidence_pct: number | null;
  withdrawn: boolean;
}

export interface PositionOut {
  id: string;
  statement_id: string;
  value: number;
  source_quote: string | null;
  source_url: string | null;
  source_date: string | null;
  confidence: string | null;
  source_type: string | null;
  notes: string | null;
}

export interface CandidateDetail {
  id: string;
  slug: string;
  name: string;
  party: string | null;
  party_acronym: string | null;
  coalition: string | null;
  bio_short: string | null;
  photo_url: string | null;
  photo_author: string | null;
  photo_license: string | null;
  photo_attribution: string | null;
  color: string | null;
  sources: Record<string, unknown> | unknown[];
  positions: PositionOut[];
  ballot_position: number | null;
  running_mate: string | null;
  positioning: string | null;
  age: number | null;
  plan_url: string | null;
  high_confidence_pct: number | null;
  withdrawn: boolean;
  withdrawn_date: string | null;
  endorses: string | null;
}

export interface StatementOut {
  id: string;
  text: string;
  category: string | null;
  slug: string | null;
  short_label: string | null;
  weight: number;
  display_order: number | null;
}

export interface QuizSubmitRequest {
  answers: Record<string, number | null>;
}

export interface CandidateAffinity {
  candidate_id: string;
  slug: string;
  name: string;
  party: string | null;
  party_acronym: string | null;
  coalition: string | null;
  photo_url: string | null;
  color: string | null;
  affinity: number;
  affinity_high_confidence: number | null;
  high_confidence_pct: number | null;
  running_mate: string | null;
  ballot_position: number | null;
}

export interface QuizResult {
  results: CandidateAffinity[];
  statements_answered: number;
}

export interface ArticleOut {
  id: string;
  slug: string;
  title: string;
  dek: string | null;
  hero_image_url: string | null;
  author: string | null;
  tags: string[] | null;
  published_at: string | null;
}

export interface ArticleDetail {
  id: string;
  slug: string;
  title: string;
  dek: string | null;
  body_markdown: string;
  hero_image_url: string | null;
  hero_image_attribution: string | null;
  author: string | null;
  tags: string[] | null;
  published_at: string | null;
}

export interface PollOut {
  id: string;
  pollster: string;
  field_start: string;
  field_end: string;
  sample_size: number | null;
  methodology: string | null;
  results: Record<string, number>;
  source_url: string | null;
  created_at: string;
}

export interface PollAverageOut {
  id: string;
  computed_at: string;
  results: Record<string, number>;
  polls_included: number | null;
}

export interface SubscriberCreate {
  email: string;
  country_code?: string | null;
  source?: string | null;
}

export interface SubscriberOut {
  id: string;
  country_code: string | null;
  status: string;
  created_at: string;
}
