import config

# Introduce a book

config.predefinedContexts["Introduce a Book"] = """Write a detailed introduction on a book in the bible, considering all the following questions:
1. Who is the author or attributed author of the book?
2. What is the date or time period when the book was written?
3. What is the main theme or purpose of the book?
4. What are the significant historical events or context surrounding the book?
5. Are there any key characters or figures in the book?
6. What are some well-known or significant passages from the book?
7. How does the book fit into the overall structure and narrative of the Bible?
8. What lessons or messages can be learned from the book?
9. What is the literary form or genre of the book (e.g. historical, prophetic, poetic, epistle, etc.)?
10. Are there any unique features or controversies surrounding the book?
I want the introduction to be comprehensive and informative.
When you explain, quote specific words or phases from relevant bible verses, if any.
Answer all these relevant questions mentioned above, in the introduction, pertaining to the following bible book."""

# Summarise a Chapter

config.predefinedContexts["Summarize a Chapter"] = """Write a detailed interpretation on a bible chapter, considering all the following questions:
1. What is the main themes or messages of the chapter?
2. What historical or cultural context is important to understand the chapter?
3. Are there any significant characters, events, or symbols in the chapter?
4. How does this chapter relate to other chapters, books, or themes in the Bible?
5. Are there any popular interpretations or controversies related to this chapter?
6. Can you provide a summary or overview of the chapter?
7. What lessons or morals can be taken from the chapter?
8. How are the verses in this chapter structured or organized?
9. Are there any key verses or passages in the chapter?
10. How have theologians, scholars, or religious leaders interpreted this chapter?
I want your interpretation to be comprehensive and informative.
When you explain, quote specific words or phases from relevant bible verses, if any.
Answer all these relevant questions mentioned above, in the interpretation, pertaining to the following bible chapter."""

# Interpret a verse

config.predefinedContexts["Interpret OT Verse"] = """Interpret the following verse in the light of its context, together with insights of biblical Hebrew studies.
I want your interpretation to be comprehensive and informative.  When you explain, quote specific words or phases from the verse.
However, remember, I want you not to quote the whole verse word by word, especially in the beginning of your response, as I already know its content."""

config.predefinedContexts["Interpret NT Verse"] = """Interpret the following verse in the light of its context, together with insights of biblical Greek studies.
I want your interpretation to be comprehensive and informative.  When you explain, quote specific words or phases from the verse.
However, remember, I want you not to quote the whole verse word by word, especially in the beginning of your response, as I already know its content."""