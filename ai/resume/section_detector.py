def detect_sections(text:str)->dict:
 t=text.lower(); keys={'contact':['email','phone','linkedin'],'summary':['summary','profile'],'education':['education','university','degree'],'experience':['experience','employment','work history'],'skills':['skills','technologies'],'projects':['projects','portfolio']}
 return {k:any(x in t for x in vs) for k,vs in keys.items()}
