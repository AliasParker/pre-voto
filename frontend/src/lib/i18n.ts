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

    // Home — global
    "home.brandTag": "Brújula electoral · Latinoamérica",
    "home.hero": "Descubrí con qué candidato coincidís.",
    "home.subtitle":
      "20 preguntas. 12 candidatos a la presidencia de Colombia. Cada posición, con su fuente.",
    "home.ctaPrimary": "Empezar el cuestionario",
    "home.ctaSecondary": "Cómo funciona",
    "home.badge1": "Independiente, sin partido",
    "home.badge2": "Cada posición con fuente",
    "home.badge3": "Sin datos personales",
    "home.badge4": "Código y datos abiertos",
    "home.viewCandidates": "Ver los 12 candidatos",
    "home.methodMeta":
      "12 candidatos · 240 posiciones documentadas · cada una con fuente verificable",
    "home.resultExampleLabel": "Ejemplo de resultado — no es un resultado real",
    "home.countriesHeader": "Próximamente en Latinoamérica",
    "home.countryActive": "activo",
    "home.microcopy":
      "No es una encuesta. No te dice por quién votar. No guardamos datos personales.",
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

    // Home — Colombia
    "home.co.title":
      "¿Orientación personal de por quién votar el 31 de mayo?",
    "home.co.subtitle":
      "Pre.voto te ayuda a comparar tus opiniones con las de los 12 candidatos a la Presidencia. 20 preguntas, 3 minutos.",
    "home.co.microcopy":
      "No es una encuesta. No te dice por quién votar. No guardamos datos personales.",

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
    "quiz.welcomeP1":
      "Vas a leer 20 afirmaciones políticas. Para cada una, decinos si estás muy de acuerdo, de acuerdo, neutral, en desacuerdo o muy en desacuerdo.",
    "quiz.welcomeP2": "No hay respuestas correctas — solo tu posición.",
    "quiz.welcomeP3":
      "Al final te mostramos qué candidato piensa parecido a vos y dónde no coinciden.",
    "quiz.howCalculated":
      "¿Cómo se calcula tu afinidad? → Ver metodología",

    // How it works
    "howItWorks.title": "Cómo funciona la brújula",
    "howItWorks.card1Title": "Vos respondés",
    "howItWorks.card1Desc":
      "20 afirmaciones políticas. Decís si estás muy de acuerdo, de acuerdo, neutral, en desacuerdo o muy en desacuerdo con cada una.",
    "howItWorks.card2Title": "Nosotros mostramos",
    "howItWorks.card2Desc":
      "La posición pública de cada uno de los 12 candidatos sobre las mismas 20 afirmaciones, con la fuente citada cuando existe.",
    "howItWorks.card3Title": "Comparamos",
    "howItWorks.card3Desc":
      "Cuanto más cerca está la posición del candidato de la tuya en cada tema, más alta es tu afinidad con él.",

    // Results
    "results.shareTitle": "Comparte tus resultados",
    "results.shareText":
      "Mi candidato más afín es {name} con {pct}%. Descubre tu afinidad en pre.voto",
    "results.newsletter": "Recibe análisis y actualizaciones",
    "results.hcLabel": "Sobre posiciones con cita directa:",
    "results.hcNone": "Sin posiciones con cita directa disponibles",
    "results.hcBadge":
      "{pct}% de sus codificaciones tienen cita directa",
    "results.hcTooltip":
      "De las 20 codificaciones de este candidato, {count} tienen cita textual directa de su plan oficial, entrevista o declaración pública. Las demás son inferencias coherentes con su trayectoria.",
    "results.lowConfCaption":
      "Este candidato tiene menos de un tercio de codificaciones con cita directa.",
    "results.lowConfLink": "Ver detalle",
    "results.zeroConfWarning":
      "{name} no tiene posiciones públicas registradas sobre 18 de los 20 temas del quiz. Las codificaciones de pre.voto son inferencias coherentes con su línea declarada, no declaraciones directas. Tu afinidad está calculada sobre esas inferencias. Para conocer su posición específica sobre cualquier tema, consultá fuentes oficiales.",

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
    "articles.subtitle":
      "Análisis y guías sobre la elección presidencial del 31 de mayo de 2026.",
    "articles.by": "Por {author}",
    "articles.publishedOn": "Publicado el {date}",
    "articles.backToArticles": "Artículos",
    "articles.noArticles": "Aún no hay artículos publicados.",
    "articles.emptyQuizLink": "Mientras tanto, puedes hacer el quiz.",
    "articles.previewBanner":
      "Vista previa — Este artículo aún no está publicado.",

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
    "disclaimer.ley2494Quiz":
      "Pre.voto es una herramienta pedagógica individual. No es una encuesta de opinión electoral en el sentido de la Ley 2494 de 2025. Tu resultado es para tu uso personal y no se agrega ni se publica como estadística colectiva. Pre.voto no mide intención de voto.",
    "disclaimer.withdrawnTitle": "Sobre el tarjetón",
    "disclaimer.withdrawnCandidates":
      "Dos candidatos del tarjetón presidencial — Clara López (casilla 2) y Luis Gilberto Murillo (casilla 14) — renunciaron a su candidatura y sus votos no se cuentan a su nombre. Pre.voto no los incluye en este quiz porque ya no están en contienda activa.",
    "disclaimer.resultsTitle": "Cómo interpretar este resultado",
    "disclaimer.resultsInterpretation":
      "Este resultado representa tu coincidencia con las posiciones declaradas o inferidas de cada candidato sobre 20 temas específicos. No es una recomendación de voto. Variables como viabilidad electoral, confianza en el equipo, manejo de crisis, o pesos personales por tema no entran al cálculo. La decisión final es tuya.",
    "disclaimer.polls":
      "Los promedios se calculan con ponderación por fecha y tamaño de muestra. Las encuestas tienen márgenes de error y limitaciones metodológicas. No son predicciones.",
    "disclaimer.methodology":
      "La metodología está en revisión continua. Si encuentras un error o quieres sugerir mejoras, abre un issue en GitHub.",

    // Candidates — withdrawn
    "candidates.withdrawnTitle": "Candidatura retirada",
    "candidates.withdrawnNotice":
      "{name} renunció a su candidatura. Su nombre permanece en el tarjetón porque ya estaba impreso, pero los votos en su casilla no se cuentan a su nombre. Sus posiciones no están codificadas en pre.voto porque ya no participa de la contienda activa.",
    "candidates.endorses":
      "{name} apoya públicamente la candidatura de {endorsee}.",

    // Veda
    "veda.title": "Jornada electoral en curso",
    "veda.heading": "El quiz está pausado temporalmente",
    "veda.body":
      "Durante la jornada electoral, la brújula de pre.voto está temporalmente inhabilitada. Podrás usarla de nuevo una vez se cierren las urnas.",
    "veda.closingTime": "Cierre de urnas: 4:00 p.m. hora Colombia",
    "veda.meanwhile": "Mientras tanto, puedes:",
    "veda.viewCandidates": "Ver las fichas de los candidatos",
    "veda.readArticles": "Leer nuestros artículos",
    "veda.quizDisabled": "La brújula estará disponible después de la jornada electoral.",
    "veda.submitBlocked":
      "El quiz está temporalmente pausado durante la jornada electoral. Intenta de nuevo después del cierre de urnas.",

    // Donations
    "donate.title": "Apoyar pre.voto",
    "donate.intro":
      "Pre.voto es una iniciativa independiente. Sin pauta comercial. Sin partido detrás. Sin contenido patrocinado.",
    "donate.body":
      "Lo construimos para que cualquier persona pueda comparar sus posiciones con las de los candidatos, con metodología abierta y verificable.",
    "donate.cta":
      "Si quieres ayudar a que sigamos haciendo esto en Brasil, México y Argentina, puedes contribuir desde acá.",
    "donate.sectionTitle": "Contribuir al proyecto",
    "donate.showCustom": "¿Otro monto?",
    "donate.hideCustom": "Ocultar",
    "donate.submit": "Contribuir",
    "donate.processing": "Procesando...",
    "donate.errorMinAmount": "El monto mínimo es $1 USD",
    "donate.errorGeneric": "No se pudo procesar la solicitud. Intenta de nuevo.",
    "donate.errorTimeout":
      "Algo salió mal. Probá de nuevo o escribinos a hola@pre.voto.",
    "donate.newsletterPostDonation":
      "Quiero recibir el newsletter mensual de pre.voto con actualizaciones del proyecto.",
    "donate.newsletterConfirm": "Confirmar",
    "donate.howTitle": "Cómo se usa el dinero",
    "donate.howBody":
      "Hosting, dominios, herramientas técnicas. Documentación y traducción de codificaciones para próximos países. Nada de salarios todavía.",
    "donate.transparencyTitle": "Transparencia",
    "donate.transparencyBody":
      "Publicaremos un reporte trimestral de ingresos y gastos. El código y las codificaciones son y serán abiertos.",
    "donate.thanksTitle": "Gracias por contribuir",
    "donate.thanksSucceeded":
      "Tu apoyo nos ayuda a llevar pre.voto a más países.",
    "donate.thanksPending":
      "Tu pago está siendo procesado. Te llegará un email de confirmación.",
    "donate.thanksFailed":
      "Hubo un problema con tu pago. Intenta de nuevo o escríbenos a hola@pre.voto.",
    "donate.confirmation": "Confirmación",
    "donate.cancelTitle": "Pago cancelado",
    "donate.cancelBody":
      "Cancelaste el pago. Si tuviste algún problema, escríbenos a hola@pre.voto.",
    "donate.backToSupport": "Volver a Apoyar",

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

    // Home — global
    "home.brandTag": "Bússola eleitoral · América Latina",
    "home.hero": "Descubra com qual candidato você coincide.",
    "home.subtitle":
      "20 perguntas. 12 candidatos à presidência da Colômbia. Cada posição, com sua fonte.",
    "home.ctaPrimary": "Começar o questionário",
    "home.ctaSecondary": "Como funciona",
    "home.badge1": "Independente, sem partido",
    "home.badge2": "Cada posição com fonte",
    "home.badge3": "Sem dados pessoais",
    "home.badge4": "Código e dados abertos",
    "home.viewCandidates": "Ver os 12 candidatos",
    "home.methodMeta":
      "12 candidatos · 240 posições documentadas · cada uma com fonte verificável",
    "home.resultExampleLabel": "Exemplo de resultado — não é um resultado real",
    "home.countriesHeader": "Em breve na América Latina",
    "home.countryActive": "ativo",
    "home.microcopy":
      "Não é uma pesquisa. Não te diz em quem votar. Não guardamos dados pessoais.",
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
    "quiz.welcomeP1":
      "Você vai ler 20 afirmações políticas. Para cada uma, diga se concorda totalmente, concorda, é neutro, discorda ou discorda totalmente.",
    "quiz.welcomeP2": "Não há respostas certas — apenas a sua posição.",
    "quiz.welcomeP3":
      "No final, mostramos qual candidato pensa parecido com você e onde não coincidem.",
    "quiz.howCalculated":
      "Como sua afinidade é calculada? → Ver metodologia",

    // How it works
    "howItWorks.title": "Como funciona a bússola",
    "howItWorks.card1Title": "Você responde",
    "howItWorks.card1Desc":
      "20 afirmações políticas. Diga se concorda totalmente, concorda, é neutro, discorda ou discorda totalmente de cada uma.",
    "howItWorks.card2Title": "Nós mostramos",
    "howItWorks.card2Desc":
      "A posição pública de cada um dos candidatos sobre as mesmas 20 afirmações, com a fonte citada quando existe.",
    "howItWorks.card3Title": "Comparamos",
    "howItWorks.card3Desc":
      "Quanto mais perto a posição do candidato está da sua em cada tema, maior é sua afinidade com ele.",

    // Results
    "results.shareTitle": "Compartilhe seus resultados",
    "results.shareText":
      "Meu candidato mais compatível é {name} com {pct}%. Descubra sua afinidade em pre.voto",
    "results.newsletter": "Receba análises e atualizações",
    "results.hcLabel": "Sobre posições com citação direta:",
    "results.hcNone": "Sem posições com citação direta disponíveis",
    "results.hcBadge":
      "{pct}% das codificações têm citação direta",
    "results.hcTooltip":
      "Das 20 codificações deste candidato, {count} têm citação textual direta de seu plano oficial, entrevista ou declaração pública. As demais são inferências coerentes com sua trajetória.",
    "results.lowConfCaption":
      "Este candidato tem menos de um terço de codificações com citação direta.",
    "results.lowConfLink": "Ver detalhe",
    "results.zeroConfWarning":
      "{name} não tem posições públicas registradas sobre 18 dos 20 temas do quiz. As codificações do pre.voto são inferências coerentes com sua linha declarada, não declarações diretas. Sua afinidade está calculada sobre essas inferências. Para conhecer sua posição específica sobre qualquer tema, consulte fontes oficiais.",

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
    "articles.subtitle":
      "Análises e guias sobre a eleição presidencial de 31 de maio de 2026.",
    "articles.by": "Por {author}",
    "articles.publishedOn": "Publicado em {date}",
    "articles.backToArticles": "Artigos",
    "articles.noArticles": "Ainda não há artigos publicados.",
    "articles.emptyQuizLink": "Enquanto isso, você pode fazer o quiz.",
    "articles.previewBanner":
      "Pré-visualização — Este artigo ainda não foi publicado.",

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
    "disclaimer.ley2494Quiz":
      "Pre.voto é uma ferramenta pedagógica individual. Não é uma pesquisa de opinião eleitoral. Seu resultado é para uso pessoal e não é agregado nem publicado como estatística coletiva. Pre.voto não mede intenção de voto.",
    "disclaimer.withdrawnTitle": "Sobre a cédula",
    "disclaimer.withdrawnCandidates":
      "Dois candidatos da cédula presidencial renunciaram à sua candidatura e seus votos não são contabilizados em seu nome. Pre.voto não os inclui neste quiz porque não estão mais na disputa ativa.",
    "disclaimer.resultsTitle": "Como interpretar este resultado",
    "disclaimer.resultsInterpretation":
      "Este resultado representa sua coincidência com as posições declaradas ou inferidas de cada candidato sobre 20 temas específicos. Não é uma recomendação de voto. Variáveis como viabilidade eleitoral, confiança na equipe, gestão de crises ou pesos pessoais por tema não entram no cálculo. A decisão final é sua.",
    "disclaimer.polls":
      "As médias são calculadas com ponderação por data e tamanho da amostra. As pesquisas possuem margens de erro e limitações metodológicas. Não são previsões.",
    "disclaimer.methodology":
      "A metodologia está em revisão contínua. Se encontrar um erro ou quiser sugerir melhorias, abra uma issue no GitHub.",

    // Candidates — withdrawn
    "candidates.withdrawnTitle": "Candidatura retirada",
    "candidates.withdrawnNotice":
      "{name} renunciou à sua candidatura. Seu nome permanece na cédula porque já estava impresso, mas os votos em sua posição não são contabilizados em seu nome. Suas posições não estão codificadas no pre.voto porque não participa mais da disputa ativa.",
    "candidates.endorses":
      "{name} apoia publicamente a candidatura de {endorsee}.",

    // Veda
    "veda.title": "Jornada eleitoral em andamento",
    "veda.heading": "O quiz está pausado temporariamente",
    "veda.body":
      "Durante a jornada eleitoral, a bússola do pre.voto está temporariamente desabilitada. Você poderá usá-la novamente após o fechamento das urnas.",
    "veda.closingTime": "Fechamento das urnas: 16:00 hora local",
    "veda.meanwhile": "Enquanto isso, você pode:",
    "veda.viewCandidates": "Ver as fichas dos candidatos",
    "veda.readArticles": "Ler nossos artigos",
    "veda.quizDisabled": "A bússola estará disponível após a jornada eleitoral.",
    "veda.submitBlocked":
      "O quiz está temporariamente pausado durante a jornada eleitoral. Tente novamente após o fechamento das urnas.",

    // Donations
    "donate.title": "Apoiar pre.voto",
    "donate.intro":
      "Pre.voto é uma iniciativa independente. Sem publicidade. Sem partido. Sem conteúdo patrocinado.",
    "donate.body":
      "Construímos para que qualquer pessoa possa comparar suas posições com as dos candidatos, com metodologia aberta e verificável.",
    "donate.cta":
      "Se você quer ajudar a levar o pre.voto para o Brasil, México e Argentina, pode contribuir por aqui.",
    "donate.sectionTitle": "Contribuir com o projeto",
    "donate.showCustom": "Outro valor?",
    "donate.hideCustom": "Ocultar",
    "donate.submit": "Contribuir",
    "donate.processing": "Processando...",
    "donate.errorMinAmount": "O valor mínimo é $1 USD",
    "donate.errorGeneric": "Não foi possível processar a solicitação. Tente novamente.",
    "donate.errorTimeout":
      "Algo deu errado. Tente de novo ou escreva para hola@pre.voto.",
    "donate.newsletterPostDonation":
      "Quero receber o newsletter mensal do pre.voto com atualizações do projeto.",
    "donate.newsletterConfirm": "Confirmar",
    "donate.howTitle": "Como o dinheiro é usado",
    "donate.howBody":
      "Hospedagem, domínios, ferramentas técnicas. Documentação e tradução de codificações para próximos países. Nenhum salário ainda.",
    "donate.transparencyTitle": "Transparência",
    "donate.transparencyBody":
      "Publicaremos um relatório trimestral de receitas e despesas. O código e as codificações são e serão abertos.",
    "donate.thanksTitle": "Obrigado por contribuir",
    "donate.thanksSucceeded":
      "Seu apoio nos ajuda a levar o pre.voto a mais países.",
    "donate.thanksPending":
      "Seu pagamento está sendo processado. Você receberá um email de confirmação.",
    "donate.thanksFailed":
      "Houve um problema com seu pagamento. Tente novamente ou escreva para hola@pre.voto.",
    "donate.confirmation": "Confirmação",
    "donate.cancelTitle": "Pagamento cancelado",
    "donate.cancelBody":
      "Você cancelou o pagamento. Se teve algum problema, escreva para hola@pre.voto.",
    "donate.backToSupport": "Voltar para Apoiar",

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
