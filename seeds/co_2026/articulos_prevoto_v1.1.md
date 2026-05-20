# Pre.voto — 5 artículos editoriales

Versión 1.2 · 19 de mayo de 2026

Este archivo contiene los 5 artículos editoriales de pre.voto para el lanzamiento en Colombia 2026, en orden de publicación. Cada artículo tiene su frontmatter Astro al inicio. Para importar al CMS: copiar cada bloque entre separadores (`---` con texto antes y después) a un archivo `.md` o `.mdx` independiente en `src/content/blog/`.

Firma editorial: todos los artículos firman como "Equipo pre.voto".

Tono: pan-LATAM neutro (tú/tienes/puedes). Las citas textuales de candidatos conservan el tono original que usaron.

---

# 1 / `metodologia.md` — publicar 23 de mayo

```yaml
---
title: "Cómo construimos pre.voto: la metodología detrás del quiz"
slug: "metodologia"
publication_date: 2026-05-23
author: "Equipo pre.voto"
country: "CO"
description: "Cada brújula electoral toma decisiones metodológicas que condicionan el resultado. Acá explicamos las nuestras, paso por paso, para que cualquier persona pueda cuestionarlas en concreto."
---
```

# Cómo construimos pre.voto: la metodología detrás del quiz

*Por Equipo pre.voto · Publicado el 23 de mayo de 2026*

**Cada brújula electoral toma decisiones metodológicas que condicionan el resultado. Qué temas se incluyen, cómo se redactan las preguntas, cómo se asigna una posición a cada candidato, qué peso lleva cada respuesta en el cálculo final. Estas decisiones no son neutras: cualquier herramienta de este tipo refleja, en su diseño, una manera de mirar la política. La diferencia entre una brújula seria y una de marketing es si esas decisiones están documentadas y son cuestionables. Esta nota explica las nuestras, paso por paso.**

## El punto de partida

Pre.voto es una *Voting Advice Application* (VAA): una herramienta que compara las posiciones del usuario con las de los candidatos en una elección. El usuario responde 20 afirmaciones, indicando su nivel de acuerdo con cada una. Al final ve un ranking de candidatos por afinidad porcentual y puede explorar tema por tema dónde coincide y dónde difiere.

El formato no es nuevo. Lo usan *Stemwijzer* en Holanda, *Wahl-O-Mat* en Alemania, *Smartvote* en Suiza, *Bússola Eleitoral* en Brasil. La literatura académica lleva dos décadas estudiando cómo se construyen, qué efectos tienen sobre los votantes, y cómo evitar los sesgos más comunes. Nosotros nos apoyamos en esa literatura para tomar nuestras decisiones.

## Paso 1: definir los 20 statements

Una brújula electoral con 50 preguntas se siente más completa pero la gente la abandona a la mitad. Una con 10 se siente liviana pero pierde resolución. Veinte es la zona de equilibrio que funciona bien en la mayoría de las brújulas comparables.

Los 20 statements de pre.voto Colombia 2026 cubren seis ejes que están definiendo la elección actual: continuidad o ruptura con el gobierno Petro (4 preguntas), paz y seguridad (4), modelo económico (4), derechos sociales (3), política exterior (2), y transición ambiental (3).

Cada statement cumple cuatro requisitos:

1. **Específico**: no se pregunta "¿está usted a favor de la seguridad?" sino "¿el pie de fuerza debe aumentarse significativamente?". Las preguntas vagas dan acuerdo unánime y no discriminan.
2. **Verificable**: el statement tiene que poder cruzarse con declaraciones públicas de los candidatos. Si ningún candidato ha hablado del tema, el statement no entra al quiz.
3. **Graduable**: cinco niveles de respuesta (muy de acuerdo, de acuerdo, neutral, en desacuerdo, muy en desacuerdo) para captar diferencias finas.
4. **Relevante para la elección actual**: temas que aparecen en debates, planes de gobierno y propuestas legislativas vigentes en 2026. No reutilizamos statements de 2018 ni de 2022.

## Paso 2: encontrar la fuente para cada posición de cada candidato

Para cada uno de los 12 candidatos en contienda activa y cada uno de los 20 statements buscamos respaldo documental, en este orden de preferencia:

1. **Plan de gobierno oficial** publicado por la campaña.
2. **Declaración pública verificable**: entrevista en medio identificable, intervención en debate, pronunciamiento en plenaria del Congreso.
3. **Cuenta oficial en redes sociales** del candidato (Twitter/X, Instagram, Facebook) o de su movimiento.
4. **Trayectoria legislativa documentada**: voto registrado, autoría de proyecto de ley, posición histórica sostenida.

Si nada de esto está disponible para un tema, la posición se infiere a partir de la línea explícita del candidato y se declara como tal. Si ni siquiera eso es posible, se marca como **neutral** con nota de "sin posición pública conocida".

## Paso 3: codificar en una escala de cinco

Cada posición se asigna a uno de cinco valores: muy de acuerdo, de acuerdo, neutral, en desacuerdo, muy en desacuerdo. La asignación no es automática. Una declaración como "la reforma pensional necesita ajustes pero no destruirla" no es "en desacuerdo" plano: es un matiz que se codifica como "en desacuerdo" o "neutral" según el contexto del resto de las declaraciones del candidato sobre el tema.

Las posiciones inferidas se asignan con un grado adicional de cautela: si la trayectoria del candidato sugiere "muy de acuerdo" pero la cita disponible no es explícita, se baja a "de acuerdo" para no sobreestimar.

## Paso 4: asignar nivel de confianza

Cada codificación lleva una etiqueta de **confianza** que informa al usuario qué tan respaldada está esa posición:

- **Alta**: cita directa al candidato sobre el tema específico del statement.
- **Media**: inferencia coherente con una línea explícita declarada (por ejemplo: el candidato declara "defender la libre empresa" y se infiere su oposición a una reforma tributaria progresiva).
- **Baja**: inferencia sin cita específica, basada en coalición o trayectoria general.

Esta información no se esconde. Cada ficha de candidato muestra cuántas de sus 20 posiciones están en cada nivel, y la página de resultados del usuario incluye una segunda métrica que calcula la afinidad usando solo las posiciones de confianza alta.

## Paso 5: revisión cruzada

Cada codificación se contrasta contra al menos una segunda fuente. Si las fuentes son consistentes, la posición se mantiene en el nivel de confianza original. Si hay contradicción entre fuentes —por ejemplo, plan de gobierno dice una cosa, declaración reciente dice otra— se prioriza la declaración más reciente y se baja la confianza a "media", con nota explícita en la ficha.

Cuando un candidato ha cambiado de posición públicamente (por ejemplo, Claudia López sobre fracking entre 2017 y 2025), la codificación refleja la posición actual con nota declarando el cambio. No se promedia entre la posición vieja y la nueva.

## Paso 6: el cálculo de afinidad

La afinidad porcentual entre el usuario y cada candidato se calcula así:

- Para cada uno de los 20 statements, se compara la respuesta del usuario con la posición codificada del candidato.
- Coincidencia exacta (mismo valor): 100 puntos para ese statement.
- Diferencia de un nivel (por ejemplo, "muy de acuerdo" vs. "de acuerdo"): 75 puntos.
- Diferencia de dos niveles: 50 puntos.
- Diferencia de tres niveles: 25 puntos.
- Diferencia de cuatro niveles (extremos opuestos): 0 puntos.

Los 20 statements se promedian con peso igual: cada uno aporta 1/20 al resultado final. No usamos pesos diferenciados por eje porque eso implicaría que pre.voto decida cuáles son los temas más importantes en la elección, y esa es una decisión que le corresponde a cada votante.

Las respuestas "neutral" del **usuario** se excluyen del cálculo (no contribuyen ni penalizan). Las respuestas "neutral" del **candidato** sí entran al cálculo, porque reflejan una posición codificada (aunque sea de ambivalencia).

## Lo que pre.voto no es

Antes de cerrar, conviene decir explícitamente lo que pre.voto no pretende ser, para que no haya malentendidos:

- **No es una encuesta** en el sentido de la Ley 2494 de 2025. No mide intención de voto, no agrega resultados, no publica estadísticas colectivas. Es una herramienta pedagógica individual.
- **No es una recomendación de voto**. La afinidad porcentual no implica que el candidato más afín sea el "correcto" para el usuario. Variables como viabilidad electoral, confianza en el equipo, manejo de crisis, o pesos personales por tema no entran al cálculo.
- **No es un medio**. No tenemos redacción, no hacemos investigaciones propias más allá de la codificación, no cubrimos la coyuntura electoral con análisis político.
- **No es definitivo**. Esta es la versión 1.0 de la metodología para Colombia 2026. Va a tener errores, ambigüedades y decisiones discutibles.

## Cómo corregir errores

El correo **errores@pre.voto** está abierto desde el día uno. Si encuentras una codificación mal interpretada, una cita desactualizada, una fuente desaparecida, o un statement ambiguo, escríbenos. Nuestro compromiso es revisar y, si la corrección procede, ajustar la base de datos en menos de 48 horas. Cuando una codificación cambia, dejamos visible cuál era la versión anterior, qué cambió, y por qué.

No vamos a defender errores que sean errores. Y no vamos a esconder los cambios.

## Por qué publicamos esto

Una brújula electoral cuya metodología vive dentro de una redacción cerrada es una caja negra. Si no puedes cuestionar las decisiones que produjeron tu resultado, no puedes decidir si confiar en el resultado. Pre.voto se construye sobre la premisa contraria: la metodología es pública porque tiene que serlo. Si no estuviéramos dispuestos a defenderla en público, no la usaríamos.

---

**Pre.voto es una iniciativa independiente, sin afiliación partidaria, sin pauta comercial y sin contenido patrocinado. Para consultas: hola@pre.voto. Para corregir errores: errores@pre.voto.**

*Este artículo está disponible bajo licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Puedes citarlo, traducirlo o republicarlo dando crédito a Equipo pre.voto.*

---

# 2 / `comparativo-cinco-candidatos.md` — publicar 24 de mayo

```yaml
---
title: "Cepeda, De la Espriella, Valencia, Fajardo y López: los cinco candidatos que se reparten el 90% del voto"
slug: "comparativo-cinco-candidatos"
publication_date: 2026-05-24
author: "Equipo pre.voto"
country: "CO"
description: "Doce candidatos en el tarjetón. Cinco concentran más del 90% de la intención de voto. Acá los ponemos lado a lado en los temas que definen la elección."
---
```

# Cepeda, De la Espriella, Valencia, Fajardo y López: los cinco candidatos que se reparten el 90% del voto

*Por Equipo pre.voto · Publicado el 24 de mayo de 2026*

**Colombia va a las urnas el 31 de mayo con 12 candidatos en el tarjetón. Pero cinco —Iván Cepeda, Abelardo de la Espriella, Paloma Valencia, Sergio Fajardo y Claudia López— concentran más del 90% de la intención de voto, según el promedio de las cinco encuestadoras nacionales. Acá los ponemos lado a lado en los temas que definen la elección: el legado de Petro, paz y seguridad, modelo económico, derechos sociales y política exterior. Sus posiciones, con cita a fuente, viven en sus fichas individuales. Esto es el mapa rápido.**

## Iván Cepeda — la continuidad del proyecto del Pacto Histórico

Senador desde 2014, hijo de un dirigente de la Unión Patriótica asesinado en 1994, defensor histórico de derechos humanos y arquitecto de la política de "Paz Total" del gobierno actual. Su candidatura nació, en parte, del juicio a Álvaro Uribe en 2025 —Cepeda fue víctima y testigo en ese caso— que lo puso en el centro del oficialismo.

Su plan de gobierno, "El poder de la verdad", tiene 433 páginas y es el más extenso de los cinco. Promete "blindar y profundizar" las reformas de Gustavo Petro: mantener la reforma pensional aprobada en 2024, implementar la reforma laboral, continuar las negociaciones con disidencias del ELN y las FARC, prohibir el fracking de forma definitiva y mantener la decisión de no fumigar con glifosato. En política exterior, daría continuidad a la línea de Petro: relaciones diplomáticas con Venezuela bajo el régimen actual, distancia con Israel, rechazo a cualquier intervención militar estadounidense en la región.

Su mayor afinidad de votante: quien apoya el proyecto del Pacto Histórico, defiende los avances en derechos sociales del actual gobierno, rechaza la militarización como respuesta al conflicto, y prioriza la transición energética sobre los hidrocarburos.

## Abelardo de la Espriella — el outsider de la mano dura

Abogado penalista de 55 años, sin trayectoria electoral previa, que irrumpió en la política con un discurso explícitamente inspirado en Nayib Bukele, Javier Milei y Donald Trump. Su movimiento se llama Defensores de la Patria y su fórmula es José Manuel Restrepo, exministro de Hacienda de Iván Duque.

Su programa, "Colombia, Patria Milagro", propone una de las rupturas más radicales: destruir 330.000 hectáreas de cultivos de coca con todas las herramientas disponibles, incluida la fumigación aérea con glifosato; reducir el tamaño del Estado en un 40%; terminar de inmediato con cualquier negociación con grupos armados ilegales; fortalecer el sector de hidrocarburos como motor económico; y oponerse frontalmente a lo que llama "el genocidio del aborto". Su plataforma se construye sobre valores explícitos: "Creemos en Dios y los valores cristianos, en la libertad plena, en el respeto a la Constitución y la ley. Defendemos la seguridad, la autoridad legítima, la libre empresa y la familia como núcleo central de la sociedad".

En política exterior, anunció en abril de 2026 una alianza pública con la opositora venezolana y Premio Nobel de la Paz 2025, María Corina Machado.

Su mayor afinidad de votante: quien quiere ruptura total con el modelo Petro, prioriza la seguridad por encima de todo, apoya la libre empresa con menos intervención estatal, defiende valores tradicionales en temas sociales y respalda alianzas explícitas con la derecha internacional.

## Paloma Valencia — la heredera del uribismo

Senadora del Centro Democrático desde 2014, abogada y filósofa, discípula declarada de Álvaro Uribe. "Seré uribista hasta que me muera y mi relación de mentoría con Álvaro Uribe prevalecerá", dijo este año. Ganó la Gran Consulta por Colombia el 8 de marzo con 3,2 millones de votos y eligió como fórmula a Juan Daniel Oviedo, exdirector del DANE de perfil técnico.

Su plan, "Colombia Más Grande 2026" o "Plan 10", combina mano dura en seguridad —Plan 30-30 para incorporar 30.000 policías y 30.000 militares, +20 billones de pesos al gasto en defensa— con propuestas técnicas en salud y economía. Reactivaría la exploración de hidrocarburos incluyendo el fracking, eliminaría el impuesto al patrimonio, propondría una reforma pensional alternativa a la de Petro y "acabaría con la paz total" para perseguir penalmente a las disidencias.

En temas sociales tiene posiciones con matices que la diferencian de De la Espriella: acepta las tres causales del aborto definidas en 2006 pero se opone a la extensión a 24 semanas de 2022; sobre la guerra en Gaza ha dicho que "la acción militar de Israel fue demasiado fuerte" y defiende la solución de dos estados.

Su mayor afinidad de votante: quien quiere reactivar la economía con menos impuestos, demanda mano firme contra el crimen organizado, comparte valores uribistas en seguridad, pero busca un tono institucional y no rupturista.

## Sergio Fajardo — el matemático del centro

Tercera campaña presidencial del exalcalde de Medellín (2004-2007) y exgobernador de Antioquia (2012-2015). Matemático con doctorado, sin partidos tradicionales detrás. Su movimiento es Dignidad y Compromiso y su fórmula es Edna Bonilla. Lleva la bandera de "una alternativa a los extremos" representados, según él, por "los señores Iván Cepeda y Abelardo de la Espriella".

Su programa, "Crisis, Esperanza, Dignidad", se ordena en 21 propuestas. Propone "acabar la paz total" pero con un tono distinto al de Valencia o De la Espriella: refuerza la fuerza pública sin retórica militarista, recuperar servicios de salud cerrados, ajustar fiscalmente sin reforma tributaria progresiva, y mantener autonomía del Banco de la República. Sobre fracking dice que "hagamos los pilotos con todo el rigor científico, y si esos pilotos nos dicen que se puede, lo hacemos. Si nos dicen que no, no se hace". Sobre el aborto: "Respeto la decisión de la Corte Constitucional". Sobre Venezuela: "establecer contactos con Venezuela, que no significa reestablecer las relaciones en el sentido pleno".

Su mayor afinidad de votante: quien rechaza la polarización, valora la gestión técnica por encima de la ideología, tiene posturas ambivalentes o "depende de" en varios temas, y prioriza educación y desarrollo regional.

## Claudia López — el centro híbrido

Exalcaldesa de Bogotá (2020-2023), primera mujer y primera lesbiana elegida para ese cargo. Líder histórica de la lucha anticorrupción —impulsó la Séptima Papeleta en 1990 que dio origen a la Constitución de 1991— y exsenadora de Alianza Verde antes de fundar su propio movimiento, Imparables. Su fórmula es Leonardo Huerta.

Su programa se organiza en tres "acuerdos": seguridad y gobernabilidad territorial, igualdad y justicia social, desarrollo regional sostenible. Propone una Fiscalía Antimafia, incorporar 40.000 miembros nuevos a la fuerza pública, llevar a escala nacional el Sistema Distrital de Cuidado que creó en Bogotá, y combatir la corrupción con sistemas de contratación 100% digitales.

Lo distintivo de López es la combinación: progresista en temas sociales (apoya plenamente la sentencia C-055/2022 sobre aborto, defiende derechos LGBTI+), pero con posturas firmes en seguridad y muy crítica con el gobierno de Maduro: "No habrá paz en Colombia mientras siga la dictadura en Venezuela", dijo en 2025, respaldando a Edmundo González y María Corina Machado. Cambió su postura sobre fracking en 2025, alejándose de la prohibición categórica que defendía en 2017.

Su mayor afinidad de votante: quien es progresista en temas culturales (aborto, LGBTI+, ambiental moderado) y al mismo tiempo demanda mano firme en seguridad y rechaza al chavismo venezolano. Es un perfil que no cubre exactamente ningún otro candidato del top 5.

## El mapa en una vista

Para que veas las diferencias de un vistazo, aquí cinco posiciones clave que separan a los candidatos:

| Tema | Cepeda | De la Espriella | Valencia | Fajardo | López |
|---|---|---|---|---|---|
| Continuidad reformas Petro | Muy a favor | Muy en contra | En contra | En contra | En contra |
| Glifosato para erradicar coca | Muy en contra | Muy a favor | Muy a favor | En contra | A favor |
| Fracking | Prohibición definitiva | Reactivar | Reactivar | Pilotos con evidencia | Sin prohibir |
| Aborto hasta 24 semanas (C-055) | Muy a favor | Muy en contra | En contra (acepta 3 causales) | A favor (respeta Corte) | Muy a favor |
| Reconocimiento al gobierno de Maduro | Mantener | No reconocer | No reconocer | Solo contactos puntuales | No reconocer |

## Cómo usar este mapa

Esto es un resumen, no un sustituto. Cada candidato tiene 20 posiciones codificadas en su ficha individual con cita a fuente: plan de gobierno oficial, declaraciones en medios verificables, pronunciamientos en cuentas oficiales. Si quieres ver el detalle expandido de un tema, entra a la ficha del candidato.

Y si quieres saber con cuál coincides más tú —no entre cinco etiquetas, sino entre 20 temas concretos donde tus posiciones se cruzan con las de cada uno—, el quiz tarda menos de cinco minutos.

Más allá del resultado, lo que importa es esto: el 31 de mayo, sea quien sea tu candidato, ve a votar. Que la elección la decidamos quienes vamos a las urnas, no la decisión que tomemos por defecto.

---

**Pre.voto es una iniciativa independiente, sin afiliación partidaria, sin pauta comercial y sin contenido patrocinado. Para consultas: hola@pre.voto.**

*Este artículo está disponible bajo licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Puedes citarlo, traducirlo o republicarlo dando crédito a Equipo pre.voto.*

---

# 3 / `otros-siete-candidatos.md` — publicar 25 de mayo

```yaml
---
title: "Más allá del top-5: los siete candidatos que también están en el tarjetón del 31 de mayo"
slug: "otros-siete-candidatos"
publication_date: 2026-05-25
author: "Equipo pre.voto"
country: "CO"
description: "Doce candidatos en el tarjetón. Cinco concentran el 90% del voto. Los otros siete, que se reparten el 10% restante y suelen quedar fuera de los debates, también merecen ser leídos antes del 31 de mayo."
---
```

# Más allá del top-5: los siete candidatos que también están en el tarjetón del 31 de mayo

*Por Equipo pre.voto · Publicado el 25 de mayo de 2026*

**El tarjetón presidencial del 31 de mayo trae 13 casillas pero 12 candidatos en contienda activa. Cinco —Cepeda, De la Espriella, Valencia, Fajardo y López— concentran más del 90% de la intención de voto y se llevan los titulares. Los otros siete se reparten el 10% restante y suelen quedar fuera de los debates de alto perfil. Pero existen, están en el tarjetón, y entender qué proponen es parte de votar informado. Acá los repasamos en orden de aparición en la boleta, con sus banderas más distintivas y dónde se ubican en el mapa político. Pre.voto también los codificó en sus 20 posiciones del quiz, aunque con un grado de evidencia disponible que varía mucho candidato por candidato. Sobre eso, al final.**

## Santiago Botero (posición 4) — el ingeniero antisistema

Empresario de 52 años, ingeniero agrónomo y fundador de Finsocial y SBO Lab. Llegó al tarjetón con 1,2 millones de firmas bajo el movimiento Romper el Sistema. Su fórmula es Carlos Fernando Cuevas, abogado y exoficial de la Armada. Su discurso es de **ultraderecha disruptiva**: pena de muerte para corruptos, violadores y asesinos seriales; una fuerza especial llamada "Templarios" con 100.000 hombres; conmoción interior para reformar el Código Penal; privatización de empresas estatales; explotación abierta de minas y petróleo. Su programa social central es Plante y Pa' Lante: entregar entre 5 y 10 millones de pesos a emprendedores. Su lema es "balín contra la corrupción". Inspiración explícita en Bukele.

Posición frente a Petro: ruptura total. Posición frente a la Paz Total: amnistía limitada hasta el 7 de agosto de 2026, después "tolerancia cero". Su voto natural: derecha más radical que aún busca un perfil más empresarial-tecnológico que el de De la Espriella.

## Mauricio Lizcano (posición 6) — el centro tech ex-Petro

49 años, abogado con maestrías en Harvard y MIT. Ex-presidente del Senado (2016-2017), ex-MinTIC y ex-DAPRE en el gobierno actual. Hoy distanciado de Petro. Llegó al tarjetón con 1,8 millones de firmas y el aval de ASI bajo la Coalición F.A.M.I.L.I.A. Su fórmula es Pedro Luis de la Torre, científico con doctorado de Harvard. Posicionamiento declarado: **"Centro Rebelde", acabar con los extremos**. "No creo en proyectos donde hay derecha e izquierda: eso es una manipulación política".

Sus banderas: emergencia humanitaria en salud (corredor humanitario de medicamentos al estilo COVID), un general activo como Ministro de Defensa, bloques de búsqueda contra la extorsión, incremento en la producción de hidrocarburos, reducción de la carga tributaria con impuestos compensatorios a juegos de azar e iglesias. Su flanco débil: ser percibido como pragmático en exceso tras pasar por gobiernos de distinto signo. Su gancho: ser uno de los pocos candidatos con experiencia ejecutiva reciente.

## Miguel Uribe Londoño (posición 7) — la tercera vía uribista

72 años, padre del senador y precandidato Miguel Uribe Turbay, asesinado el 11 de agosto de 2025. Economista de la Universidad de Miami y abogado de los Andes. Fue precandidato del Centro Democrático tras la muerte de su hijo, pero **expulsado del partido en febrero de 2026** en medio de un conflicto interno con Álvaro Uribe. Relanzó su candidatura con el aval del Partido Demócrata Colombiano. Su fórmula es Luisa Fernanda Villegas.

Su discurso es de continuidad explícita con el legado político de su hijo: "Mi primer decreto será acabar con la Paz Total". Plan de seguridad con 260.000 cámaras y plataformas de analítica predictiva. Reforma laboral para reducir cargas no salariales en micro y pequeñas empresas. Ha declarado que respaldaría a Abelardo de la Espriella en segunda vuelta si no llega él mismo, "para impedir que Cepeda sea presidente". Su voto natural: uribistas que sienten que Paloma Valencia se "amplió" demasiado al centro al aliarse con Juan Daniel Oviedo.

## Sondra Macollins (posición 8) — la abogada de hierro independiente

51 años, abogada penalista (Universidad Libre + LL.M de St. John's en Nueva York). Sin trayectoria política previa (fue candidata a la Cámara por Colombianos en el Exterior en 2022). Llegó al tarjetón con 1,13 millones de firmas bajo el Partido Digital. Su fórmula es Leonardo Karam Helo, abogado especializado en seguridad pública. Se autopercibe como **centro independiente "sin jefes políticos, sin partidos tradicionales"**.

Su propuesta más comentada: eliminar progresivamente las 32 gobernaciones y asambleas departamentales, y reemplazarlas por 7 grandes regiones con presupuesto propio, parlamentos regionales y autoridades elegidas por voto. Argumenta que las gobernaciones son "un peaje al desarrollo". Su lema: "Menos política, más tecnología". Su debilidad pública más visible: tiene pocas posiciones públicas sobre los temas tradicionales del debate (Paz Total, hidrocarburos, derechos sociales). Su campaña gira casi entera alrededor de la reestructuración territorial.

## Roy Barreras (posición 9) — el médico ex-aliado de Petro

62 años, médico de profesión, exsenador desde 2006, ex-presidente del Congreso en 2012 y 2022, exembajador en el Reino Unido. Ganó la consulta del Frente por la Vida el 8 de marzo de 2026 con 207.000 votos. Su fórmula es Martha Lucía Zamora. Posicionamiento: **centro-izquierda con énfasis tecnológico**, ex-aliado de Petro hoy distanciado.

Su plan tiene cuatro motores: tecnología transversal ("Gobierno sin filas" — digitalización total del Estado), infraestructura logística (Renacimiento Ferroviario, Corredor Multimodal Interoceánico en el Darién/Chocó), seguridad con 10.000 drones inteligentes monitoreados con IA, y cultura como pilar económico (Mochila Digital para artistas). Su gancho técnico: Historia Clínica Única Nacional con blockchain. Su flanco: ha planteado abiertamente la posibilidad de una "revolución del voto en blanco" como hipótesis, lo que sus contrincantes leyeron como reconocimiento de que no tiene caminos electorales reales.

## Carlos Caicedo (posición 10) — el candidato del Caribe

60 años, abogado y exrector de la Universidad del Magdalena, exalcalde de Santa Marta y exgobernador del Magdalena. Su movimiento es Fuerza Ciudadana y su fórmula es Nelson Javier Alarcón. Posicionamiento: **izquierda no-Petro, candidato de las regiones**, eje en federalismo. Crítico del centralismo tanto en gobiernos de izquierda como de derecha.

Su propuesta estrella: pagar medio salario mínimo mensual a estudiantes de grados 10 y 11 (o a sus familias) para frenar la deserción y el reclutamiento por grupos armados. "Por cada cien jóvenes que entran al sistema educativo, no llegan ni a 20 los que salen graduados". Mínimo vital gratuito en servicios públicos. En seguridad propone aumentar el número de policías y soldados y mejorar los salarios de la fuerza pública para reducir corrupción interna. Su base electoral está concentrada en el Caribe colombiano. Su flanco débil: investigaciones judiciales vigentes sobre su paso por la Alcaldía de Santa Marta, que él presenta como "persecución de los clanes tradicionales".

## Gustavo Matamoros (posición 11) — el general del orden

71 años, general retirado del Ejército Nacional con 40+ años de carrera. Hijo del exministro de Defensa Gustavo Matamoros D'Costa. Participó en la planeación de la Operación Jaque en 2008 (rescate de Íngrid Betancourt y otros 14 secuestrados de las FARC) y la Operación Sodoma en 2010 (muerte de alias "Mono Jojoy"). Llegó al tarjetón en marzo de 2026 reemplazando a Maurice Armitage en el aval del Partido Ecologista. Su fórmula es Mila María Paz Campaz, lideresa afrodescendiente del Pacífico.

Lema de campaña: **"se acabó el desorden"**. Tres pilares declarados: seguridad, sobriedad y salud. Desmontaría las mesas de negociación con grupos armados el 7 de agosto, día uno del gobierno, y las reemplazaría por una ley de sometimiento con reparación a víctimas, entrega de rutas del narcotráfico y cumplimiento de penas. Sobre la justicia transicional fue tajante: "En mi gobierno, la JEP se acaba". Aunque tiene el aval del Partido Ecologista —por sustitución, no por afinidad ambiental previa— su plataforma no ha desarrollado una agenda verde robusta. Su voto natural: derecha que prioriza la mano militar pero rechaza la retórica más confrontativa de De la Espriella.

## Una nota honesta sobre el quiz y estos siete candidatos

Pre.voto codificó a los 12 candidatos en contienda activa en los mismos 20 temas, con la misma metodología. Pero el grado de evidencia disponible varía mucho, tanto entre candidatos del top como entre los minoritarios.

Para los cinco candidatos del top, el 52% de las codificaciones se hicieron con **cita directa al candidato** (plan de gobierno oficial, declaración en medios verificable, pronunciamiento en cuenta oficial). Pero ese promedio esconde diferencias importantes: Cepeda llega al 85% y De la Espriella al 80%, mientras que Fajardo está en el 30% y López en el 45%, no por falta de información política sobre ellos sino porque sus posiciones se infirieron de trayectoria y entrevistas no específicas más que de propuestas escritas tema por tema.

Para los siete candidatos que cubrimos en este artículo, el porcentaje de codificaciones con cita directa baja al 14% en promedio. La diferencia no es de método sino de materia prima: estos candidatos sencillamente no han hablado en público sobre la mayoría de los temas del quiz. Muchos centraron toda su campaña en una o dos banderas (la reestructuración territorial para Macollins, la mano dura para Matamoros, los "Templarios" para Botero).

El caso más extremo es el de Sondra Macollins. Sus 20 codificaciones son inferencias —ninguna se basa en cita directa, porque la candidata no ha tomado posición pública sobre la mayoría de los temas del quiz. Su campaña se ha centrado casi enteramente en una propuesta: la reestructuración territorial. Por eso su ficha en pre.voto incluye un aviso reforzado declarando que la afinidad que calculamos contigo es, en su caso, una aproximación cautelosa basada en su línea declarada, no en posiciones específicas que ella haya defendido sobre cada tema.

Por eso cada ficha en pre.voto muestra **el porcentaje de posiciones con cita directa vs. inferidas**. Cuando hagas el quiz y veas tu afinidad con un candidato minoritario, ese número va con su disclaimer al lado. La afinidad se calcula con todas las posiciones, pero también se muestra una segunda métrica: la afinidad sólo con las posiciones citadas. Tú decides cuál te importa.

## Por qué cubrirlos

Cubrir solo a los cinco favoritos haría a pre.voto cómplice de una elección reducida desde antes de votar. Hay ciudadanos cuya afinidad genuina está en un candidato que las encuestas marcan al 1%. Eso no es marginal: es información. Y en el cierre, el mensaje sigue siendo el de siempre: el 31 de mayo, sea quien sea tu candidato, ve a votar.

---

**Pre.voto es una iniciativa independiente, sin afiliación partidaria, sin pauta comercial y sin contenido patrocinado. Para consultas: hola@pre.voto.**

*Este artículo está disponible bajo licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Puedes citarlo, traducirlo o republicarlo dando crédito a Equipo pre.voto.*

---

# 4 / `como-se-vota.md` — publicar 26 de mayo

```yaml
---
title: "Cómo se vota el 31 de mayo: guía rápida del sistema electoral colombiano"
slug: "como-se-vota"
publication_date: 2026-05-26
author: "Equipo pre.voto"
country: "CO"
description: "Guía corta y desideologizada de lo que conviene saber antes de salir al puesto de votación. Dónde, cuándo, cómo se cuenta, qué pasa con el voto en blanco."
---
```

# Cómo se vota el 31 de mayo: guía rápida del sistema electoral colombiano

*Por Equipo pre.voto · Publicado el 26 de mayo de 2026*

**Faltan cinco días para la primera vuelta presidencial. Más de 41.4 millones de colombianos están habilitados para votar. Esta es una guía corta y desideologizada de lo que conviene saber antes de salir al puesto, sin importar a quién pienses votar: dónde, cuándo, cómo se cuenta, qué pasa con el voto en blanco y con las casillas de quienes renunciaron, qué dice la Ley 2494 sobre lo que se puede y no se puede publicar antes del día de la elección, y qué viene después.**

## Cuándo y dónde

El domingo 31 de mayo de 2026, **de 8:00 de la mañana a 4:00 de la tarde**, en todo el país y en consulados habilitados en el exterior. El horario es estricto: si a las 4:00 p.m. estás en la fila pero aún no has llegado a la mesa, la Registraduría confirmó que **no podrás votar**. Esto sirve también de aviso práctico: ve temprano.

Antes de salir verifica tu puesto en la página oficial de la Registraduría —el portal pide cédula y un código de seguridad y devuelve departamento, municipio, dirección del puesto y número de mesa. El plazo para cambiar el puesto por cambio de residencia ya cerró el 31 de marzo, así que tu mesa es la que figure hoy en el censo electoral. Si cambiaste de ciudad después de marzo, te toca votar en el puesto antiguo.

Los únicos dos documentos válidos para votar son la **cédula amarilla con hologramas** o la **cédula digital** en la aplicación oficial. Pasaporte, licencia de conducción o contraseña no sirven. La Registraduría instalará un total de **120.527 mesas en 13.742 puestos de votación** distribuidos en todo el territorio nacional y en consulados en el exterior.

## Cómo se vota

El tarjetón tiene **13 casillas** ordenadas por sorteo de la Registraduría, más una casilla adicional para el **voto en blanco**. Solo se puede marcar una opción: si marcas más de una, el voto se anula. La marcación correcta es una equis o una mancha clara dentro de la casilla del candidato que eliges.

Hay una particularidad importante de este tarjetón: dos casillas corresponden a candidatos que **renunciaron después del inicio de la impresión** y cuya foto quedó en la boleta. Clara López (casilla 2) renunció el 6 de abril para sumarse a la campaña de Iván Cepeda; su espacio fue retirado del tarjetón final. Luis Gilberto Murillo (casilla 14) renunció más tarde, cuando los tarjetones ya estaban impresos, y por eso su foto sigue ahí. **Los votos que reciban estos candidatos retirados no se cuentan a su nombre** y no se transfieren a Cepeda: se contabilizan como votos no válidos. En total quedan **12 candidatos en contienda activa**.

## Cómo se decide quién gana

En Colombia, para ganar la elección presidencial en **primera vuelta** un candidato necesita más del **50% de los votos válidos** —es decir, al menos la mitad más uno, dejando por fuera los votos nulos y los no marcados. Si ningún candidato lo logra, los dos más votados pasan a una **segunda vuelta**, programada para el **domingo 21 de junio de 2026**, también de 8 a 4.

En las últimas tres elecciones presidenciales (2014, 2018, 2022) hubo segunda vuelta. Las encuestas previas a esta jornada apuntan al mismo escenario.

## El voto en blanco y para qué sirve

El **voto en blanco** no es un voto nulo ni un acto de protesta sin efecto: es una opción **constitucionalmente reconocida** que se marca en una casilla específica del tarjetón. Está regulada por el artículo 258 de la Constitución, reformado por el Acto Legislativo 01 de 2009.

La regla es esta: si el voto en blanco obtiene la **mayoría absoluta de los votos válidos** en una primera vuelta presidencial, la elección **se repite por una única vez** y los candidatos que se presentaron en la elección anulada **no pueden volver a presentarse**. Es decir: si más de la mitad de los votos válidos del 31 de mayo fueran en blanco, habría una nueva primera vuelta con candidatos distintos. En la práctica esto nunca ha pasado en una elección presidencial colombiana, pero la opción está legalmente disponible.

Importante: **esta regla solo aplica a la primera vuelta**. En la eventual segunda vuelta del 21 de junio el voto en blanco se contabiliza pero no tiene el efecto de anular la elección. En segunda vuelta gana, sin importar el porcentaje, quien obtenga la mayor cantidad de votos válidos entre los dos candidatos en contienda.

## La veda electoral y la Ley 2494

Desde el **24 de mayo** y hasta el cierre de las mesas el 31 de mayo, en Colombia está vigente la **veda de publicación de encuestas presidenciales** —ocho días, según lo establece la regulación electoral. Los medios y casas encuestadoras no pueden divulgar nuevos sondeos sobre intención de voto durante ese período. Las encuestas se siguen haciendo, pero no se publican.

El día de la elección —domingo 31 de mayo— hay además una **veda de propaganda electoral**: no se puede hacer campaña activa en la vía pública, en redes sociales con cuentas oficiales de campaña, ni en medios de comunicación. La Ley Seca también es habitual en muchos municipios desde el sábado.

La **Ley 2494 de 2025**, aprobada el año pasado, reguló específicamente las encuestas, los sondeos y las herramientas digitales que pretenden medir opinión electoral. Esta ley establece requisitos de metodología, ficha técnica obligatoria, registro de encuestadoras y sanciones por incumplimiento.

Pre.voto se acoge a esta regulación con una declaración explícita: **pre.voto no es una encuesta**. Es una herramienta pedagógica individual que le permite a un usuario comparar sus posiciones con las codificadas de cada candidato. Pre.voto no publica agregados de "porcentaje de usuarios con afinidad a X candidato" ni difunde estimaciones de intención de voto. Es una calculadora personal, no un termómetro electoral. La diferencia es importante legalmente y editorialmente: una encuesta predice; una brújula electoral compara.

## Qué pasa después del 31 de mayo

La Registraduría comienza la transmisión de resultados preliminares pocas horas después del cierre de las mesas, alrededor de las 5 de la tarde. Esa noche habrá un **preconteo** con los datos que llegan desde las mesas y el escrutinio oficial sigue en los días siguientes hasta consolidarse en el escrutinio nacional. Históricamente la diferencia entre preconteo y escrutinio definitivo en elecciones presidenciales colombianas es de pocas décimas porcentuales.

Si ningún candidato supera el 50% de los votos válidos, la segunda vuelta será el **21 de junio**. La toma de posesión del nuevo presidente y vicepresidente, según el calendario constitucional, será el **7 de agosto de 2026** en la Plaza de Armas de la Casa de Nariño.

## El certificado electoral y los beneficios de votar

Quien vote recibe en su puesto un **certificado electoral** físico, que en Colombia da derecho a:

- Medio día compensatorio de descanso laboral remunerado, a tomar dentro de los 45 días posteriores a la elección
- Descuentos en trámites de cédula y pasaporte
- Rebaja del 10% en la matrícula de instituciones de educación superior pública
- Prioridad en concursos de carrera administrativa del Estado en caso de empate
- Descuentos en algunos trámites notariales

El certificado se entrega físicamente el día de la votación. Conservarlo conviene.

## Una nota final

Pre.voto es una herramienta para llegar al puesto con más información sobre cuál es tu afinidad con cada candidato. No es un sustituto del criterio individual, de la lectura del plan de gobierno, ni del debate con tu gente. Lo que sí pretende es que el 31 de mayo nadie llegue a la urna con la sensación de que está votando a ciegas.

Ve temprano, lleva la cédula amarilla o digital, verifica el puesto antes de salir y, sea cual sea tu candidato, **vota**. La elección la decidimos quienes vamos a las urnas.

---

**Pre.voto es una iniciativa independiente, sin afiliación partidaria, sin pauta comercial y sin contenido patrocinado. Para consultas: hola@pre.voto.**

*Este artículo está disponible bajo licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Puedes citarlo, traducirlo o republicarlo dando crédito a Equipo pre.voto.*

---

# 5 / `lanzamiento.md` — publicar 27 de mayo

```yaml
---
title: "Por qué construimos pre.voto: una brújula electoral pan-LATAM, sin medio detrás"
slug: "lanzamiento"
publication_date: 2026-05-27
author: "Equipo pre.voto"
country: "CO"
description: "Hoy lanzamos pre.voto en Colombia. Una brújula electoral que compara tus posiciones con las de los 12 candidatos. Acá explicamos por qué lo hicimos y qué viene después de la primera vuelta."
---
```

# Por qué construimos pre.voto: una brújula electoral pan-LATAM, sin medio detrás

*Por Equipo pre.voto · Publicado el 27 de mayo de 2026*

**Hoy lanzamos pre.voto en Colombia, a cuatro días de la primera vuelta presidencial del 31 de mayo. Es una brújula electoral —lo que la literatura académica llama una *Voting Advice Application* o VAA— que compara tus posiciones con las de los 12 candidatos en contienda activa sobre los 20 temas que más están definiendo esta elección. Es gratis. Toma menos de cinco minutos. La metodología es pública y cada posición de cada candidato está respaldada por una fuente citada o, cuando no la hay, declarada como inferencia. Después de Colombia, vienen Brasil, México y Argentina. Esta nota explica por qué lo hicimos, qué tiene de distinto, y qué prometemos —y qué no prometemos— para los próximos meses.**

## El problema que pre.voto intenta resolver

Las brújulas electorales existen hace dos décadas. En Holanda, *Stemwijzer* fue usada por casi la mitad del electorado nacional en la elección de 2021. En Alemania, *Wahl-O-Mat* es una institución cívica del Bundeszentrale für politische Bildung. En Suiza, *Smartvote*. En Brasil, *Bússola Eleitoral*. Son herramientas reconocidas, estudiadas, citadas por la prensa, usadas por partidos como referencia.

En América Latina la oferta es desigual y dispersa. Brasil tiene un par de iniciativas serias pero con audiencias acotadas. México no tiene una brújula electoral consolidada para sus elecciones federales. Argentina nunca ha tenido una en elecciones presidenciales con cobertura significativa. Colombia, en 2026, tiene a Candidateados (con apoyo de la Unión Europea), el test electoral de El Tiempo, una iniciativa de Publimetro con IA, y KeepUp/Uniandes (que se concentra en el Senado).

Todas son aportes valiosos. Pero **ninguna cubre los 12 candidatos completos** del tarjetón presidencial colombiano: la mayoría se limita a los cinco favoritos. **Ninguna publica metodología abierta con cita a fuente por posición**: las codificaciones quedan dentro de redacciones o equipos académicos cerrados. **Ninguna es regional**: no existe hoy una brújula electoral pan-LATAM, hecha con la misma metodología en países distintos para que un ciudadano pueda compararse con candidatos de Colombia, Brasil, México y Argentina sin cambiar de herramienta. Y **todas las que tienen tracción real tienen un medio detrás**: un periódico, una universidad, un canal de televisión.

Eso no es malo, pero crea un hueco. Pre.voto entra a llenarlo.

## Qué hicimos

Para Colombia 2026 codificamos a los 12 candidatos en contienda activa sobre 20 temas que cubren seis ejes: continuidad o ruptura con el gobierno actual, paz y seguridad, modelo económico, derechos sociales, política exterior, y transición ambiental. En total son **240 codificaciones** —20 posiciones por candidato— cada una con una fuente pública verificable o, cuando esa fuente no existe, una declaración explícita de que la posición fue inferida con un grado de confianza menor.

Para los cinco candidatos con mayor intención de voto, en promedio el 52% de las codificaciones se apoya en cita directa al candidato: plan de gobierno oficial, entrevista verificable, pronunciamiento en cuenta verificada. Ese promedio esconde una variación importante entre candidatos: va desde el 85% de Iván Cepeda hasta el 30% de Sergio Fajardo, dependiendo de cuán explícito sea cada candidato en sus propuestas escritas. Para los siete candidatos minoritarios, ese porcentaje baja al 14% en promedio —no por falta de método sino porque no han hablado en público sobre la mayoría de los temas. Todo eso lo declaramos abiertamente en cada ficha, y cada usuario ve, junto a su porcentaje de afinidad con un candidato, el nivel de respaldo documental de las codificaciones detrás de ese cálculo.

El quiz te muestra 20 afirmaciones y te pide que indiques tu nivel de acuerdo con cada una. Al final calcula tu afinidad porcentual con cada uno de los 12 candidatos, en orden de mayor a menor, y te permite ver tema por tema dónde coincides y dónde difieres. La página de resultados tiene dos números visibles para cada candidato: tu afinidad calculada con todas las posiciones, y tu afinidad calculada solo con las posiciones que tienen cita directa. Tú decides cuál te importa más.

## Por qué Colombia primero

Cuatro razones. Primera, **escala**: 41 millones de votantes habilitados, una elección altamente polarizada, primera transición presidencial después del gobierno de Gustavo Petro. Segunda, **timing**: la veda de publicación de encuestas, vigente desde el 24 de mayo, crea un hueco informativo de ocho días que herramientas como pre.voto —que no son encuestas— pueden ayudar a cubrir con información orientadora individual. Tercera, **marco legal claro**: la Ley 2494 de 2025 define con precisión qué es una encuesta y qué no lo es, y pre.voto opera dentro de la categoría de herramientas pedagógicas individuales. Y cuarta, **idioma**: español, que comparte con tres de los próximos cuatro países donde queremos lanzar.

## Por qué la región, y no un solo país

El mismo problema se repite en cada elección presidencial latinoamericana. Muchos candidatos, polarización fuerte, cobertura mediática asimétrica que se concentra en los dos o tres más visibles, fragmentación de la oferta informativa para el ciudadano que quiere votar con criterio.

Después de Colombia, el calendario que nos pusimos es **Brasil para la elección presidencial de octubre de 2026**, después **México para su elección intermedia y de gobernaturas en 2027**, y después **Argentina para su elección presidencial del mismo año**. Cada país tiene sus 20 statements propios —ningún quiz es portable entre países sin reescribirlo desde cero porque las elecciones se juegan sobre temas distintos— pero la metodología, la transparencia de fuentes, la declaración de niveles de confianza y la independencia editorial son las mismas.

Un usuario en Bogotá, en São Paulo, en Ciudad de México y en Buenos Aires va a encontrar la misma herramienta. La afinidad va a calcularse igual. La pregunta sobre quién financia el proyecto va a tener la misma respuesta. Esa es la apuesta.

## Quiénes somos y qué no somos

Pre.voto es un proyecto **pequeño, sin pauta comercial, sin contenido patrocinado, financiado por las contribuciones voluntarias de quienes lo apoyan**. No recibimos financiamiento de partidos políticos ni de campañas. No vendemos publicidad. No aceptamos dinero de fondos cuyo objetivo declarado o evidente sea la injerencia electoral.

Lo que sí aceptamos es feedback metodológico de académicos, periodistas y ciudadanos. Lo que sí queremos es que las correcciones de errores sean inmediatas y públicas: el correo **errores@pre.voto** está abierto desde el día uno, y nuestro compromiso es responder y corregir —si la corrección procede— en menos de 48 horas, con la modificación documentada en el repositorio público de metodología. Cuando una codificación cambie por evidencia nueva, vamos a decir qué cambió, por qué cambió, y dejar el cambio visible.

No tenemos lista de aliados famosos, ni respaldo institucional, ni una redacción detrás. Tenemos una herramienta y una metodología, y ambas están abiertas para que cualquier persona —incluido cualquier crítico— las pueda examinar.

## Estamos en beta y lo decimos abiertamente

Esta es la versión 1.0 de pre.voto. 240 codificaciones para 12 candidatos es mucho material, y algunas de esas codificaciones van a estar mal interpretadas. Algunos statements del quiz van a ser ambiguos para algunos lectores. Algunas fuentes van a quedar desactualizadas en los próximos días si un candidato cambia de posición.

Nada de eso es excusa. Lo que ofrecemos es transparencia sobre el proceso de corrección. Si encuentras un error —en una codificación, en una cita, en una fuente, en la redacción de un statement— escríbenos a errores@pre.voto y lo arreglamos. Si tu argumento es que una posición está mal interpretada, muéstranos la fuente que la respalda mejor y la revisamos. Si tu objeción es metodológica, el documento público de metodología está en el sitio para discutirlo en concreto.

No vamos a defender errores que sean errores. Y no vamos a esconder los cambios.

## El cierre

Si pre.voto te resulta útil, haz el quiz, compártelo con tu gente, mándanos críticas concretas. Si no te resulta útil, critícalo, escríbelo, recomienda una mejor alternativa —las hay, y son buenas. En cualquier caso, lo que más importa pasa el domingo 31 de mayo en el puesto de votación.

Que la elección la decidamos quienes vamos a votar, no la decisión que tomemos por defecto. Ve a votar, sea quien sea tu candidato.

Pre.voto Colombia abre hoy. Brasil, México y Argentina vienen después.

---

**Pre.voto es una iniciativa independiente, sin afiliación partidaria, sin pauta comercial y sin contenido patrocinado. Para consultas: hola@pre.voto. Para corregir errores: errores@pre.voto. La metodología completa, los 20 statements y las codificaciones de los 12 candidatos están disponibles en pre.voto/metodologia.**

*Este artículo está disponible bajo licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Puedes citarlo, traducirlo o republicarlo dando crédito a Equipo pre.voto.*