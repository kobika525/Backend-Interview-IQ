def extract_skills(text:str,known:list[str])->list[str]:
 t=text.lower(); return sorted({s for s in known if s.lower() in t})
