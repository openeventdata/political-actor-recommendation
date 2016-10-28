#Automatic Political Actor Recommendation In Real-Time
 
This tool can be used to recommend popular actors based on the newspaper articles collected within a time-span. Here is the abstract of the related 
paper.
```
  Extracting a structured representation of events (political, social etc.) has become an interesting domain in the 
  computational and social sciences. One approach is to use dictionary-based pattern look-ups to identify actors and 
  actions involved in potential events represented in who-did-what-to-whom format (e.g., CAMEO). A key complication 
  of this approach is updating the dictionaries with new actors (e.g., when a new president takes office). Currently, 
  the dictionaries are curated by humans, updated infrequently, and at high cost. This means that tools dependent on 
  the dictionaries (e.g., PETRARCH) overlook events because they are missing dictionary entries. In this paper, we 
  address how to extend the dictionaries used to identify actors. We proposed a frequency-based actor ranking algorithm 
  using partial string matching-based (e.g., Levenshtein/Edit distance, MinHash, etc.) actor grouping for dynamic new 
  actor recommendations over multiple time windows. Moreover, we suggest the associated evolving role of recommended 
  actors from the role of co-related political actors in the existing CAMEO actor dictionary. Experiments show a high
   percentage of the recommended actors are retained after end-user feedback. 
```

## Input

The tool takes newspaper articles as input, divided into several files (we consider them windows). Each of the file contains Core NLP parsed
newsa articles.

A sample data-set can be found here: https://utdallas.box.com/s/33bue9ci9241v1btuwozsh8mfh1rda1i
 
## Output
The output of the tool is set of possible political actors and suggestion of a list of roles for each of them.


## Requirement

The tool has following requirements - 
- Named Entity Recognition in Core NLP parse of an article.
- PETRARCH2 output which contains nouns that PETRARCH2 found inside each sentence.
 
 


