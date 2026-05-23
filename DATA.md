# pre.voto — Open Data

## Dataset

Pre.voto publishes its editorial data under **CC-BY 4.0**. The dataset covers the 2026 Colombian presidential election:

- **20 statements** — policy questions spanning 6 thematic axes
- **12 active candidates** (+ 2 withdrawn) — with party, coalition, and positioning
- **240 candidate-statement positions** — each with value, confidence level, source type, and source citation

## API endpoints

All endpoints are public (no auth), return JSON, and include `X-License: CC-BY-4.0` and `Access-Control-Allow-Origin: *` headers.

### GET `/api/opendata/co/statements`

All quiz statements for Colombia 2026.

Fields: `slug`, `text`, `category`, `short_label`, `weight`, `display_order`

```bash
curl https://pre.voto/api/opendata/co/statements
```

### GET `/api/opendata/co/candidates`

All candidates for the active election.

Fields: `slug`, `name`, `party`, `party_acronym`, `coalition`, `bio_short`, `photo_url`, `color`, `ballot_position`, `positioning`, `high_confidence_pct`, `withdrawn`, `withdrawn_date`, `endorses`

```bash
curl https://pre.voto/api/opendata/co/candidates
```

### GET `/api/opendata/co/positions`

All 240 candidate-statement positions (flat join).

Fields: `candidate_slug`, `candidate_name`, `statement_slug`, `statement_text`, `statement_category`, `value`, `value_label`, `confidence`, `source_type`, `source_quote`, `source_url`, `source_date`

```bash
curl https://pre.voto/api/opendata/co/positions
```

## Attribution

If you use this data, include the following attribution:

> Equipo pre.voto, [pre.voto](https://pre.voto), CC-BY 4.0

## Electoral freeze

During the 7 days before an active election, editorial data is frozen. The API remains available but positions are not updated until after the election.

## License

- **Editorial data**: CC-BY 4.0
- **Code**: AGPL-3.0-or-later

See [LICENSE](./LICENSE) for full terms.
