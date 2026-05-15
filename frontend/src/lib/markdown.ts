import { marked } from "marked";

marked.setOptions({
  breaks: true,
  gfm: true,
});

/**
 * Render Markdown string to sanitized HTML.
 * Used for article body rendering at build time.
 */
export function renderMarkdown(markdown: string): string {
  return marked.parse(markdown, { async: false }) as string;
}
