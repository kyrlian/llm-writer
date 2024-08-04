prompts = {
    "English": {
        "prompt_summarize": "Please summarize the following TEXT in one or two sentences, do no add comments:\n\nTEXT\n\n{tmptext}\n",
        "prompt_suggest": "Please read the STORY SO FAR below, and the provided INSTRUCTIONS, then please complete the story following the provided instructions. Do not add comments, only print the summary.\n\nSTORY SO FAR\n\n{fullsummary}\n\nINSTRUCTIONS\n\n{instructions}\n",
    },
    "French": {
        "prompt_summarize": "Veuillez résumer le TEXTE suivant en une ou deux phrases, sans ajouter de commentaires :\n\nTEXTE\n\n{tmptext}\n",
        "prompt_suggest": "Veuillez lire l'HISTOIRE JUSQUE ICI ci-dessous et les INSTRUCTIONS fournies, puis complétez l'histoire en suivant les instructions fournies. N'ajoutez pas de commentaires, affichez seulement le résumé.\n\nHISTOIRE JUSQUE ICI\n\n{fullsummary}\n\nINSTRUCTIONS\n\n{instructions}\n",
    },
}