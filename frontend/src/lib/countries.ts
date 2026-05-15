import type { Locale } from "./i18n";

export interface CountryMeta {
  name: Record<Locale, string>;
  flag: string;
  locale: Locale;
  active: boolean;
}

export const countries: Record<string, CountryMeta> = {
  co: {
    name: { es: "Colombia", "pt-BR": "Colombia" },
    flag: "\uD83C\uDDE8\uD83C\uDDF4",
    locale: "es",
    active: true,
  },
  mx: {
    name: { es: "Mexico", "pt-BR": "Mexico" },
    flag: "\uD83C\uDDF2\uD83C\uDDFD",
    locale: "es",
    active: false,
  },
  ar: {
    name: { es: "Argentina", "pt-BR": "Argentina" },
    flag: "\uD83C\uDDE6\uD83C\uDDF7",
    locale: "es",
    active: false,
  },
  cl: {
    name: { es: "Chile", "pt-BR": "Chile" },
    flag: "\uD83C\uDDE8\uD83C\uDDF1",
    locale: "es",
    active: false,
  },
  pe: {
    name: { es: "Peru", "pt-BR": "Peru" },
    flag: "\uD83C\uDDF5\uD83C\uDDEA",
    locale: "es",
    active: false,
  },
  br: {
    name: { es: "Brasil", "pt-BR": "Brasil" },
    flag: "\uD83C\uDDE7\uD83C\uDDF7",
    locale: "pt-BR",
    active: false,
  },
};

export function getCountryName(code: string, locale: Locale): string {
  const meta = countries[code];
  if (!meta) return code.toUpperCase();
  return meta.name[locale] ?? meta.name.es;
}
