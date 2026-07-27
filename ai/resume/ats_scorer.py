import re
def score(text,sections,matched_required,total_required):
 required=100*matched_required/max(total_required,1); section=100*sum(sections.values())/len(sections); keywords=min(100,len(set(re.findall(r'[a-zA-Z]{4,}',text)))/3); quantified=min(100,len(re.findall(r'\d+%?|\$\d+',text))*15); action=sum(text.lower().count(x) for x in ['built','developed','improved','created','led','implemented']); action=min(100,action*12); formatting=100 if len(text)>300 else 50; experience=100 if sections['experience'] else 30; education=100 if sections['education'] else 30
 cats={'required_skills':required,'role_keywords':keywords,'section_completeness':section,'experience_relevance':experience,'formatting_readiness':formatting,'education_relevance':education,'achievement_quality':(quantified+action)/2}
 weights={'required_skills':.30,'role_keywords':.20,'section_completeness':.15,'experience_relevance':.15,'formatting_readiness':.10,'education_relevance':.05,'achievement_quality':.05}
 return round(sum(cats[k]*weights[k] for k in weights),2),{k:round(v,2) for k,v in cats.items()}
