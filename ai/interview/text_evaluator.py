import re
def evaluate(answer:str,keywords:list[str],behavioral:bool=False):
 t=answer.lower(); coverage=100*sum(1 for k in keywords if k.lower() in t)/max(len(keywords),1); completeness=min(100,len(answer.split())*2); clarity=max(20,100-min(70,answer.count(' um ')*8+answer.count(' uh ')*8)); relevance=(coverage+completeness)/2
 star={k:any(c in t for c in cues) for k,cues in {'situation':['situation','when','context'],'task':['task','responsible','goal'],'action':['action','i did','implemented'],'result':['result','outcome','improved']}.items()}; star_score=25*sum(star.values()) if behavioral else None
 final=.45*relevance+.25*coverage+.20*clarity+.10*completeness
 if behavioral: final=.35*relevance+.25*star_score+.20*clarity+.10*coverage+.10*completeness
 cats={'relevance':round(relevance,2),'keyword_coverage':round(coverage,2),'clarity':round(clarity,2),'completeness':round(completeness,2)}
 if star_score is not None: cats['star_structure']=star_score
 return round(final,2),cats,{'word_count':len(answer.split()),'star':star},(['Relevant key points were included'] if coverage>=50 else []),(['Add more role-specific evidence'] if coverage<50 else [])
