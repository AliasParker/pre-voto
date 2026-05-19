export type Locale = "es" | "pt-BR";

const translations: Record<Locale, Record<string, string>> = {
  es: {
    // Nav
    "nav.home": "Inicio",
    "nav.howItWorks": "Cómo funciona",
    "nav.methodology": "Metodología",
    "nav.about": "Sobre",
    "nav.privacy": "Privacidad",

    // Common
    "common.backToHome": "Volver al inicio",
    "common.readMore": "Leer más",
    "common.loading": "Cargando...",
    "common.error": "Ha ocurrido un error",
    "common.soon": "Próximamente",
    "common.minutes": "minutos",
    "common.source": "Fuente",
    "common.date": "Fecha",
    "common.share": "Compartir",
    "common.copyLink": "Copiar enlace",
    "common.copied": "¡Copiado!",
    "common.electionDay": "Día de elecciones",
    "common.electionEnded": "Elección finalizada",
    "common.days": "días",
    "common.hours": "horas",
    "common.mins": "min",
    "common.secs": "seg",

    // Home
    "home.hero": "Voto informado para Latinoamérica.",
    "home.subtitle":
      "Compara tus posiciones con las de los candidatos. Sin registro, sin datos personales, procesado en tu navegador.",
    "home.howItWorks": "Cómo funciona",
    "home.step1Title": "Responde el cuestionario",
    "home.step1Desc":
      "Evalúa {count} afirmaciones sobre políticas públicas en una escala de 5 puntos.",
    "home.step2Title": "Compara tu posición",
    "home.step2Desc":
      "Un algoritmo transparente calcula tu afinidad con cada candidato.",
    "home.step3Title": "Vota informado",
    "home.step3Desc":
      "Revisa las fuentes, profundiza en los temas y toma tu decisión.",
    "home.upcomingElections": "Próximas elecciones",
    "home.selectCountry": "Selecciona tu país",

    // Country
    "country.startQuiz": "Hacer la brújula electoral",
    "country.viewCandidates": "Ver candidatos",
    "country.viewPolls": "Ver encuestas",
    "country.readAnalysis": "Leer análisis",
    "country.latestArticles": "Últimos artículos",
    "country.pollSummary": "Resumen de encuestas",
    "country.noArticles": "Aún no hay artículos publicados.",
    "country.noPolls": "Aún no hay datos de encuestas.",

    // Quiz
    "quiz.title": "Brújula Electoral",
    "quiz.welcome": "Descubre tu afinidad con los candidatos",
    "quiz.welcomeDesc":
      "Responde a una serie de afirmaciones sobre políticas públicas y descubre qué candidato se alinea más con tus valores.",
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
    "quiz.back": "Atrás",
    "quiz.restart": "Volver a empezar",
    "quiz.yourResults": "Tus resultados",
    "quiz.affinity": "afinidad",
    "quiz.statementBreakdown": "Detalle por afirmación",
    "quiz.yourAnswer": "Tu respuesta",
    "quiz.candidatePosition": "Posición del candidato",
    "quiz.noPosition": "Sin posición registrada",

    // Results
    "results.shareTitle": "Comparte tus resultados",
    "results.shareText":
      "Mi candidato más afín es {name} con {pct}%. Descubre tu afinidad en pre.voto",
    "results.newsletter": "Recibe análisis y actualizaciones",

    // Shared result
    "shared.title": "Resultado compartido",
    "shared.cta": "¿Quieres descubrir tu afinidad con los candidatos?",

    // Newsletter
    "newsletter.title": "Mantente informado",
    "newsletter.desc":
      "Recibe análisis, actualizaciones de encuestas y recordatorios electorales.",
    "newsletter.placeholder": "tu@email.com",
    "newsletter.submit": "Suscribirse",
    "newsletter.success": "Te has suscrito exitosamente.",
    "newsletter.error": "No se pudo completar la suscripción. Intenta de nuevo.",
    "newsletter.rateLimit": "Demasiados intentos. Intenta más tarde.",

    // Candidates
    "candidates.title": "Candidatos",
    "candidates.positions": "Posiciones",
    "candidates.affinityQuestion": "¿Qué tan afín eres?",
    "candidates.takeQuiz": "Hacer la brújula electoral",
    "candidates.photoAttribution": "Foto: {author} ({license})",

    // Articles
    "articles.title": "Artículos",
    "articles.by": "Por {author}",
    "articles.noArticles": "Aún no hay artículos publicados.",

    // Polls
    "polls.title": "Encuestas",
    "polls.average": "Promedio de encuestas",
    "polls.chart": "Tendencia histórica",
    "polls.table": "Encuestas individuales",
    "polls.pollster": "Encuestadora",
    "polls.fieldDate": "Fecha de campo",
    "polls.sampleSize": "Muestra",
    "polls.noPolls": "Aún no hay datos de encuestas.",

    // Footer
    "footer.license": "Contenido bajo licencia CC-BY 4.0",
    "footer.github": "Código fuente",
    "footer.description":
      "Brújula electoral independiente para Latinoamérica. Compara tus posiciones con las de los candidatos.",
    "footer.navTitle": "Navegación",
    "footer.contactTitle": "Contacto",
    "footer.support": "Apoyar",
    "footer.independence":
      "Pre.voto es una iniciativa independiente, sin afiliación partidaria, sin pauta comercial y sin contenido patrocinado. Para consultas: hola@pre.voto. Para corregir errores: errores@pre.voto.",
    "footer.ley2494":
      "Pre.voto NO es una encuesta de opinión electoral en el sentido de la Ley 2494 de 2025. Es una herramienta pedagógica individual.",

    // Disclaimer
    "disclaimer.quiz":
      "Esta herramienta es un instrumento pedagógico, no una encuesta ni una recomendación de voto. Los resultados reflejan la cercanía entre tus respuestas y las posiciones documentadas de los candidatos. Verifica siempre las fuentes originales.",
    "disclaimer.polls":
      "Los promedios se calculan con ponderación por fecha y tamaño de muestra. Las encuestas tienen márgenes de error y limitaciones metodológicas. No son predicciones.",
    "disclaimer.methodology":
      "La metodología está en revisión continua. Si encuentras un error o quieres sugerir mejoras, abre un issue en GitHub.",

    // Position values
    "position.-2": "Totalmente en desacuerdo",
    "position.-1": "En desacuerdo",
    "position.0": "Neutral",
    "position.1": "De acuerdo",
    "position.2": "Totalmente de acuerdo",
  },
  "pt-BR": {
    // Nav
    "nav.home": "Início",
    "nav.howItWorks": "Como funciona",
    "nav.methodology": "Metodologia",
    "nav.about": "Sobre",
    "nav.privacy": "Privacidade",

    // Common
    "common.backToHome": "Voltar ao início",
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
    "common.electionDay": "Dia da eleição",
    "common.electionEnded": "Eleição encerrada",
    "common.days": "dias",
    "common.hours": "horas",
    "common.mins": "min",
    "common.secs": "seg",

    // Home
    "home.hero": "Voto informado para a América Latina.",
    "home.subtitle":
      "Compare suas posições com as dos candidatos. Sem cadastro, sem dados pessoais, processado no seu navegador.",
    "home.howItWorks": "Como funciona",
    "home.step1Title": "Responda o questionário",
    "home.step1Desc":
      "Avalie {count} afirmações sobre políticas públicas em uma escala de 5 pontos.",
    "home.step2Title": "Compare sua posição",
    "home.step2Desc":
      "Um algoritmo transparente calcula sua afinidade com cada candidato.",
    "home.step3Title": "Vote informado",
    "home.step3Desc":
      "Revise as fontes, aprofunde-se nos temas e tome sua decisão.",
    "home.upcomingElections": "Próximas eleições",
    "home.selectCountry": "Selecione seu país",

    // Country
    "country.startQuiz": "Fazer a bússola eleitoral",
    "country.viewCandidates": "Ver candidatos",
    "country.viewPolls": "Ver pesquisas",
    "country.readAnalysis": "Ler análises",
    "country.latestArticles": "Últimos artigos",
    "country.pollSummary": "Resumo das pesquisas",
    "country.noArticles": "Ainda não há artigos publicados.",
    "country.noPolls": "Ainda não há dados de pesquisas.",

    // Quiz
    "quiz.title": "Bússola Eleitoral",
    "quiz.welcome": "Descubra sua afinidade com os candidatos",
    "quiz.welcomeDesc":
      "Responda a uma série de afirmações sobre políticas públicas e descubra qual candidato mais se alinha com seus valores.",
    "quiz.time": "~3 minutos",
    "quiz.noRegistration": "Sem cadastro",
    "quiz.localProcessing": "Processado no seu navegador",
    "quiz.start": "Começar",
    "quiz.questionOf": "Pergunta {current} de {total}",
    "quiz.stronglyAgree": "Concordo totalmente",
    "quiz.agree": "Concordo",
    "quiz.neutral": "Neutro",
    "quiz.disagree": "Discordo",
    "quiz.stronglyDisagree": "Discordo totalmente",
    "quiz.back": "Voltar",
    "quiz.restart": "Recomeçar",
    "quiz.yourResults": "Seus resultados",
    "quiz.affinity": "afinidade",
    "quiz.statementBreakdown": "Detalhes por afirmação",
    "quiz.yourAnswer": "Sua resposta",
    "quiz.candidatePosition": "Posição do candidato",
    "quiz.noPosition": "Sem posição registrada",

    // Results
    "results.shareTitle": "Compartilhe seus resultados",
    "results.shareText":
      "Meu candidato mais compatível é {name} com {pct}%. Descubra sua afinidade em pre.voto",
    "results.newsletter": "Receba análises e atualizações",

    // Shared result
    "shared.title": "Resultado compartilhado",
    "shared.cta": "Quer descobrir sua afinidade com os candidatos?",

    // Newsletter
    "newsletter.title": "Fique informado",
    "newsletter.desc":
      "Receba análises, atualizações de pesquisas e lembretes eleitorais.",
    "newsletter.placeholder": "seu@email.com",
    "newsletter.submit": "Inscrever-se",
    "newsletter.success": "Você se inscreveu com sucesso.",
    "newsletter.error": "Não foi possível completar a inscrição. Tente novamente.",
    "newsletter.rateLimit": "Muitas tentativas. Tente mais tarde.",

    // Candidates
    "candidates.title": "Candidatos",
    "candidates.positions": "Posições",
    "candidates.affinityQuestion": "Qual a sua afinidade?",
    "candidates.takeQuiz": "Fazer a bússola eleitoral",
    "candidates.photoAttribution": "Foto: {author} ({license})",

    // Articles
    "articles.title": "Artigos",
    "articles.by": "Por {author}",
    "articles.noArticles": "Ainda não há artigos publicados.",

    // Polls
    "polls.title": "Pesquisas",
    "polls.average": "Média das pesquisas",
    "polls.chart": "Tendência histórica",
    "polls.table": "Pesquisas individuais",
    "polls.pollster": "Instituto",
    "polls.fieldDate": "Data de campo",
    "polls.sampleSize": "Amostra",
    "polls.noPolls": "Ainda não há dados de pesquisas.",

    // Footer
    "footer.license": "Conteúdo sob licença CC-BY 4.0",
    "footer.github": "Código fonte",
    "footer.description":
      "Bússola eleitoral independente para a América Latina. Compare suas posições com as dos candidatos.",
    "footer.navTitle": "Navegação",
    "footer.contactTitle": "Contato",
    "footer.support": "Apoiar",
    "footer.independence":
      "Pre.voto é uma iniciativa independente, sem afiliação partidária, sem publicidade e sem conteúdo patrocinado. Para consultas: hola@pre.voto. Para corrigir erros: errores@pre.voto.",
    "footer.ley2494":
      "Pre.voto NÃO é uma pesquisa de opinião eleitoral. É uma ferramenta pedagógica individual.",

    // Disclaimer
    "disclaimer.quiz":
      "Esta ferramenta é um instrumento pedagógico, não uma pesquisa nem uma recomendação de voto. Os resultados refletem a proximidade entre suas respostas e as posições documentadas dos candidatos. Verifique sempre as fontes originais.",
    "disclaimer.polls":
      "As médias são calculadas com ponderação por data e tamanho da amostra. As pesquisas possuem margens de erro e limitações metodológicas. Não são previsões.",
    "disclaimer.methodology":
      "A metodologia está em revisão contínua. Se encontrar um erro ou quiser sugerir melhorias, abra uma issue no GitHub.",

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
