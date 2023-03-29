import config

# General

config.predefinedContexts["Word Meaning"] = """What is the meaning of the following word or words?"""
config.predefinedContexts["Meaning in the Bible"] = """What is the meaning of the following content in reference to the Bible?"""
config.predefinedContexts["Write a Summary"] = """Write a summary on the following content."""
config.predefinedContexts["Write a Sermon"] = """Write a sermon on the following content in reference to the Bible."""
config.predefinedContexts["Write a Prayer"] = """Write a summary on the following content in reference to the Bible."""
config.predefinedContexts["Key Words"] = """Identify key words in the following content.
Elaborate on their importance in comprehending the context and the bible as a whole.
I want your elaboration to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing."""
config.predefinedContexts["Key Themes"] = """Identify key themes or key messages in the following content.
Elaborate on their importance in comprehending the content and the bible as a whole.
I want your elaboration to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing."""
config.predefinedContexts["Bible Topic"] = """Write about the following topic in reference to the Bible.
In addition, explain the significance of the topic in the bible.
I want your writing to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing."""
config.predefinedContexts["Bible Theology"] = """Please write the theological messages conveyed in the content below, in reference to the Bible.
In addition, explain the significance of the theological messages in the bible.
I want your writing to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing."""
config.predefinedContexts["Bible Place"] = """I will provide you with a location name.
Give me comprehensive information on this location in the bible.
If this singular name is used to denote various different locations in the Bible, kindly provide separate descriptions for each one.
Explain the significance of this location in the bible."""
config.predefinedContexts["Bible Person"] = """I will provide you with a person name.
Give me comprehensive information on this person in the bible.
If this singular name is used to denote various different characters in the Bible, kindly provide separate descriptions for each one.
Explain the significance of this person in the bible."""
config.predefinedContexts["Bible Promises"] = """Please provide me with Bible verses that contain promises and can serve as an encouragement to people, specifically in relation to the given content."""

# Translation

config.predefinedContexts["Translate Content"] = """I want you to assist me as a translator.
I will provide content below for your translation.
After I provide you with the content, you will ask me what language I want it translated to.
I will respond, and you can proceed with the translation.
Please translate the content below."""
config.predefinedContexts["Translate Hebrew Verse"] = """I would like to request your assistance as a bible translator.
I will provide you with Hebrew bible verses one by one, and kindly ask that you translate each verse in accordance with its context within the passage.
In addition, I want you to map each Hebrew word with corresponding translation.
Please also include transliteration or pronunciation guide of each Hebrew word in your mapping.
Use "Translation" and "Mapping" as the section titles.
Remember, do not give explanation or repeat the bible reference that I give you."""
config.predefinedContexts["Translate Greek Verse"] = """I would like to request your assistance as a bible translator.
I will provide you with Greek bible verses one by one, and kindly ask that you translate each verse in accordance with its context within the passage.
In addition, I want you to map each Greek word with corresponding translation.
Please also include transliteration or pronunciation guide of each Greek word in your mapping.
Use "Translation" and "Mapping" as the section titles.
Remember, do not give explanation or repeat the bible reference that I give you."""

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