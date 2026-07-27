def ok(data=None,message='Operation completed successfully'): return {'success':True,'message':message,'data':data if data is not None else {}}
def pagination(page,page_size,total):
 import math
 pages=math.ceil(total/page_size) if total else 0
 return {'page':page,'page_size':page_size,'total_items':total,'total_pages':pages,'has_next':page<pages,'has_previous':page>1}
