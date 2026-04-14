import spacy

nlp = spacy.load("es_core_news_sm")

def detectar_actores(pregunta):
    doc = nlp(pregunta)
    actores = []

    for ent in doc.ents:
        if ent.label_ == "PER":
            actores.append(ent.text.lower())

    return actores


def interpretar_actores(pregunta):
    actores = detectar_actores(pregunta)

    incluir = None
    excluir = None

    if len(actores) == 1:
        incluir = actores[0]

    elif len(actores) >= 2:
        incluir = actores[0]

        if "no" in pregunta or "sin" in pregunta:
            excluir = actores[1]

    return incluir, excluir