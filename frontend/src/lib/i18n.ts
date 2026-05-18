export type Locale = "es" | "pt-BR";

const translations: Record<Locale, Record<string, string>> = {
  es: {
    // Nav
    "nav.home": "Inicio",
    "nav.howItWorks": "Como funciona",
    "nav.methodology": "Metodologia",
    "nav.about": "Sobre",
    "nav.privacy": "Privacidad",

    // Common
    "common.backToHome": "Volver al inicio",
    "common.readMore": "Leer mas",
    "common.loading": "Cargando...",
    "common.error": "Ha ocurrido un error",
    "common.soon": "Proximamente",
    "common.minutes": "minutos",
    "common.source": "Fuente",
    "common.date": "Fecha",
    "common.share": "Compartir",
    "common.copyLink": "Copiar enlace",
    "common.copied": "Copiado!",
    "common.electionDay": "Dia de elecciones",
    "common.electionEnded": "Eleccion finalizada",
    "common.days": "dias",
    "common.hours": "horas",
    "common.mins": "min",
    "common.secs": "seg",

    // Home
    "home.hero": "Voto informado para Latinoamerica.",
    "home.subtitle":
      "Compara tus posiciones con las de los candidatos. Sin registro, sin datos personales, procesado en tu navegador.",
    "home.howItWorks": "Como funciona",
    "home.step1Title": "Responde el cuestionario",
    "home.step1Desc":
      "Evalua {count} afirmaciones sobre politicas publicas en una escala de 5 puntos.",
    "home.step2Title": "Compara tu posicion",
    "home.step2Desc":
      "Un algoritmo transparente calcula tu afinidad con cada candidato.",
    "home.step3Title": "Vota informado",
    "home.step3Desc":
      "Revisa las fuentes, profundiza en los temas y toma tu decision.",
    "home.upcomingElections": "Proximas elecciones",
    "home.selectCountry": "Selecciona tu pais",

    // Country
    "country.startQuiz": "Hacer la brujula electoral",
    "country.viewCandidates": "Ver candidatos",
    "country.viewPolls": "Ver encuestas",
    "country.readAnalysis": "Leer analisis",
    "country.latestArticles": "Ultimos articulos",
    "country.pollSummary": "Resumen de encuestas",
    "country.noArticles": "Aun no hay articulos publicados.",
    "country.noPolls": "Aun no hay datos de encuestas.",

    // Quiz
    "quiz.title": "Brujula Electoral",
    "quiz.welcome": "Descubre tu afinidad con los candidatos",
    "quiz.welcomeDesc":
      "Responde a una serie de afirmaciones sobre politicas publicas y descubre que candidato se alinea mas con tus valores.",
    "quiz.time": "~3 minutos",
    "quiz.noRegistration": "Sin registro",
    "quiz.localProcessing": "Procesado en tu navegador",
    "quiz.start": "Comenzar",
    "quiz.questionOf": "Pregunta {current} de {total}",
    "quiz.stronglyAgree": "Totalmente de acuerdo",
    "quiz.agree": "De acuerdo",
    "quiz.neutral": "Neutral",
    "quiz.disagree": "En desacuerdo",
    "quiz.stronglyDisagree": "Totalmente en desacuerdo",
    "quiz.back": "Atras",
    "quiz.restart": "Volver a empezar",
    "quiz.yourResults": "Tus resultados",
    "quiz.affinity": "afinidad",
    "quiz.statementBreakdown": "Detalle por afirmacion",
    "quiz.yourAnswer": "Tu respuesta",
    "quiz.candidatePosition": "Posicion del candidato",
    "quiz.noPosition": "Sin posicion registrada",

    // Results
    "results.shareTitle": "Comparte tus resultados",
    "results.shareText":
      "Mi candidato mas afin es {name} con {pct}%. Descubre tu afinidad en pre.voto",
    "results.newsletter": "Recibe analisis y actualizaciones",

    // Shared result
    "shared.title": "Resultado compartido",
    "shared.cta": "Quieres descubrir tu afinidad con los candidatos?",

    // Newsletter
    "newsletter.title": "Mantente informado",
    "newsletter.desc":
      "Recibe analisis, actualizaciones de encuestas y recordatorios electorales.",
    "newsletter.placeholder": "tu@email.com",
    "newsletter.submit": "Suscribirse",
    "newsletter.success": "Te has suscrito exitosamente.",
    "newsletter.error": "No se pudo completar la suscripcion. Intenta de nuevo.",
    "newsletter.rateLimit": "Demasiados intentos. Intenta mas tarde.",

    // Candidates
    "candidates.title": "Candidatos",
    "candidates.positions": "Posiciones",
    "candidates.affinityQuestion": "Que tan afin eres?",
    "candidates.takeQuiz": "Hacer la brujula electoral",
    "candidates.photoAttribution": "Foto: {author} ({license})",

    // Articles
    "articles.title": "Articulos",
    "articles.by": "Por {author}",
    "articles.noArticles": "Aun no hay articulos publicados.",

    // Polls
    "polls.title": "Encuestas",
    "polls.average": "Promedio de encuestas",
    "polls.chart": "Tendencia historica",
    "polls.table": "Encuestas individuales",
    "polls.pollster": "Encuestadora",
    "polls.fieldDate": "Fecha de campo",
    "polls.sampleSize": "Muestra",
    "polls.noPolls": "Aun no hay datos de encuestas.",

    // Footer
    "footer.license": "Contenido bajo licencia CC-BY 4.0",
    "footer.github": "Codigo fuente",

    // Disclaimer
    "disclaimer.quiz":
      "Esta herramienta es un instrumento pedagogico, no una encuesta ni una recomendacion de voto. Los resultados reflejan la cercania entre tus respuestas y las posiciones documentadas de los candidatos. Verifica siempre las fuentes originales.",
    "disclaimer.polls":
      "Los promedios se calculan con ponderacion por fecha y tamano de muestra. Las encuestas tienen margenes de error y limitaciones metodologicas. No son predicciones.",
    "disclaimer.methodology":
      "La metodologia esta en revision continua. Si encuentras un error o quieres sugerir mejoras, abre un issue en GitHub.",

    // Position values
    "position.-2": "Totalmente en desacuerdo",
    "position.-1": "En desacuerdo",
    "position.0": "Neutral",
    "position.1": "De acuerdo",
    "position.2": "Totalmente de acuerdo",
  },
  "pt-BR": {
    // Nav
    "nav.home": "Inicio",
    "nav.howItWorks": "Como funciona",
    "nav.methodology": "Metodologia",
    "nav.about": "Sobre",
    "nav.privacy": "Privacidade",

    // Common
    "common.backToHome": "Voltar ao inicio",
    "common.readMore": "Ler mais",
    "common.loading": "Carregando...",
    "common.error": "Ocorreu um erro",
    "common.soon": "Em breve",
    "common.minutes": "minutos",
    "common.source": "Fonte",
    "common.date": "Data",
    "common.share": "Compartilhar",
    "common.copyLink": "Copiar link",
    "common.copied": "Copiado!",
    "common.electionDay": "Dia da eleicao",
    "common.electionEnded": "Eleicao encerrada",
    "common.days": "dias",
    "common.hours": "horas",
    "common.mins": "min",
    "common.secs": "seg",

    // Home
    "home.hero": "Voto informado para a America Latina.",
    "home.subtitle":
      "Compare suas posicoes com as dos candidatos. Sem cadastro, sem dados pessoais, processado no seu navegador.",
    "home.howItWorks": "Como funciona",
    "home.step1Title": "Responda o questionario",
    "home.step1Desc":
      "Avalie {count} afirmacoes sobre politicas publicas em uma escala de 5 pontos.",
    "home.step2Title": "Compare sua posicao",
    "home.step2Desc":
      "Um algoritmo transparente calcula sua afinidade com cada candidato.",
    "home.step3Title": "Vote informado",
    "home.step3Desc":
      "Revise as fontes, aprofunde-se nos temas e tome sua decisao.",
    "home.upcomingElections": "Proximas eleicoes",
    "home.selectCountry": "Selecione seu pais",

    // Country
    "country.startQuiz": "Fazer a bussola eleitoral",
    "country.viewCandidates": "Ver candidatos",
    "country.viewPolls": "Ver pesquisas",
    "country.readAnalysis": "Ler analises",
    "country.latestArticles": "Ultimos artigos",
    "country.pollSummary": "Resumo das pesquisas",
    "country.noArticles": "Ainda nao ha artigos publicados.",
    "country.noPolls": "Ainda nao ha dados de pesquisas.",

    // Quiz
    "quiz.title": "Bussola Eleitoral",
    "quiz.welcome": "Descubra sua afinidade com os candidatos",
    "quiz.welcomeDesc":
      "Responda a uma serie de afirmacoes sobre politicas publicas e descubra qual candidato mais se alinha com seus valores.",
    "quiz.time": "~3 minutos",
    "quiz.noRegistration": "Sem cadastro",
    "quiz.localProcessing": "Processado no seu navegador",
    "quiz.start": "Comecar",
    "quiz.questionOf": "Pergunta {current} de {total}",
    "quiz.stronglyAgree": "Concordo totalmente",
    "quiz.agree": "Concordo",
    "quiz.neutral": "Neutro",
    "quiz.disagree": "Discordo",
    "quiz.stronglyDisagree": "Discordo totalmente",
    "quiz.back": "Voltar",
    "quiz.restart": "Recomecar",
    "quiz.yourResults": "Seus resultados",
    "quiz.affinity": "afinidade",
    "quiz.statementBreakdown": "Detalhes por afirmacao",
    "quiz.yourAnswer": "Sua resposta",
    "quiz.candidatePosition": "Posicao do candidato",
    "quiz.noPosition": "Sem posicao registrada",

    // Results
    "results.shareTitle": "Compartilhe seus resultados",
    "results.shareText":
      "Meu candidato mais compativel e {name} com {pct}%. Descubra sua afinidade em pre.voto",
    "results.newsletter": "Receba analises e atualizacoes",

    // Shared result
    "shared.title": "Resultado compartilhado",
    "shared.cta": "Quer descobrir sua afinidade com os candidatos?",

    // Newsletter
    "newsletter.title": "Fique informado",
    "newsletter.desc":
      "Receba analises, atualizacoes de pesquisas e lembretes eleitorais.",
    "newsletter.placeholder": "seu@email.com",
    "newsletter.submit": "Inscrever-se",
    "newsletter.success": "Voce se inscreveu com sucesso.",
    "newsletter.error": "Nao foi possivel completar a inscricao. Tente novamente.",
    "newsletter.rateLimit": "Muitas tentativas. Tente mais tarde.",

    // Candidates
    "candidates.title": "Candidatos",
    "candidates.positions": "Posicoes",
    "candidates.affinityQuestion": "Qual a sua afinidade?",
    "candidates.takeQuiz": "Fazer a bussola eleitoral",
    "candidates.photoAttribution": "Foto: {author} ({license})",

    // Articles
    "articles.title": "Artigos",
    "articles.by": "Por {author}",
    "articles.noArticles": "Ainda nao ha artigos publicados.",

    // Polls
    "polls.title": "Pesquisas",
    "polls.average": "Media das pesquisas",
    "polls.chart": "Tendencia historica",
    "polls.table": "Pesquisas individuais",
    "polls.pollster": "Instituto",
    "polls.fieldDate": "Data de campo",
    "polls.sampleSize": "Amostra",
    "polls.noPolls": "Ainda nao ha dados de pesquisas.",

    // Footer
    "footer.license": "Conteudo sob licenca CC-BY 4.0",
    "footer.github": "Codigo fonte",

    // Disclaimer
    "disclaimer.quiz":
      "Esta ferramenta e um instrumento pedagogico, nao uma pesquisa nem uma recomendacao de voto. Os resultados refletem a proximidade entre suas respostas e as posicoes documentadas dos candidatos. Verifique sempre as fontes originais.",
    "disclaimer.polls":
      "As medias sao calculadas com ponderacao por data e tamanho da amostra. As pesquisas possuem margens de erro e limitacoes metodologicas. Nao sao previsoes.",
    "disclaimer.methodology":
      "A metodologia esta em revisao continua. Se encontrar um erro ou quiser sugerir melhorias, abra uma issue no GitHub.",

    // Position values
    "position.-2": "Discordo totalmente",
    "position.-1": "Discordo",
    "position.0": "Neutro",
    "position.1": "Concordo",
    "position.2": "Concordo totalmente",
  },
};

/**
 * Get a translated string with optional parameter interpolation.
 * Keys use dot notation: t('es', 'nav.home')
 * Parameters use {placeholder} syntax: t('es', 'quiz.questionOf', { current: 1, total: 8 })
 */
export function t(
  locale: Locale,
  key: string,
  params?: Record<string, string | number>,
): string {
  const dict = translations[locale] ?? translations.es;
  let value = dict[key] ?? translations.es[key] ?? key;
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      value = value.replace(`{${k}}`, String(v));
    }
  }
  return value;
}

/**
 * Map country code to locale.
 * Brazil → pt-BR, everything else → es
 */
export function getLocaleFromCountry(code: string): Locale {
  if (code === "br") return "pt-BR";
  return "es";
}
