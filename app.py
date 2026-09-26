import os,re,base64,json,statistics,requests
from pathlib import Path
from typing import Optional
from fastapi import FastAPI,UploadFile,File,Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
BASE_DIR=Path(__file__).resolve().parent
app=FastAPI(title='PorCuanto WebApp')
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY',''); OPENAI_MODEL=os.getenv('OPENAI_MODEL','gpt-5.6-luna'); OPENAI_TIMEOUT=float(os.getenv('OPENAI_TIMEOUT','18'))
KEEPA_API_KEY=os.getenv('KEEPA_API_KEY',''); EBAY_CLIENT_ID=os.getenv('EBAY_CLIENT_ID',''); EBAY_CLIENT_SECRET=os.getenv('EBAY_CLIENT_SECRET',''); EBAY_MARKETPLACE_ID=os.getenv('EBAY_MARKETPLACE_ID','EBAY_ES')
UPCITEMDB_URL='https://api.upcitemdb.com/prod/trial/lookup'
BARCODELOOKUP_API_KEY=os.getenv('BARCODELOOKUP_API_KEY','')

MARKETS={
 'ES':('🇪🇸','Amazon.es','amazon.es',9,'EUR'),'DE':('🇩🇪','Amazon.de','amazon.de',3,'EUR'),'FR':('🇫🇷','Amazon.fr','amazon.fr',4,'EUR'),'IT':('🇮🇹','Amazon.it','amazon.it',8,'EUR'),'UK':('🇬🇧','Amazon.co.uk','amazon.co.uk',2,'GBP'),
 'NL':('🇳🇱','Amazon.nl','amazon.nl',None,'EUR'),'BE':('🇧🇪','Amazon.com.be','amazon.com.be',None,'EUR'),'PL':('🇵🇱','Amazon.pl','amazon.pl',None,'PLN'),'SE':('🇸🇪','Amazon.se','amazon.se',None,'SEK'),'IE':('🇮🇪','Amazon.ie','amazon.ie',None,'EUR'),'TR':('🇹🇷','Amazon.com.tr','amazon.com.tr',None,'TRY')}
# Compatibilidad: la V18 sirve los recursos desde la raíz para facilitar la subida a GitHub.
if (BASE_DIR/'static').exists():
    app.mount('/static',StaticFiles(directory=str(BASE_DIR/'static')),name='static')
def eur(v): return round(float(v),2) if v is not None else None
def cents(v): return eur(v/100) if isinstance(v,(int,float)) and v>=0 else None
def get_asin(v):
 m=re.search(r'(?:dp/|gp/product/|product/)([A-Z0-9]{10})|\b(B0[A-Z0-9]{8})\b',v or '',re.I); return (m.group(1) or m.group(2)).upper() if m else None
def get_code(v):
 m=re.search(r'\b\d{8,14}\b',v or ''); return m.group() if m else None
def upcitemdb_lookup(code):
    """Resolve EAN/UPC/GTIN through UPCitemdb's free trial endpoint.
    The free Explorer currently allows lookup without registration, so this is
    an automatic accelerator rather than a required user API key.
    """
    code=get_code(str(code or ''))
    if not code:return {}
    try:
        rr=requests.get(UPCITEMDB_URL,params={'upc':code},headers={'Accept':'application/json','User-Agent':'PorCuanto/25'},timeout=10)
        if rr.status_code==200:
            d=rr.json() or {}; item=(d.get('items') or [None])[0]
            if item:
                offers=item.get('offers') or []
                prices=[]
                for o in offers:
                    try:
                        v=float(o.get('price'))
                        if 0<v<100000: prices.append(v)
                    except: pass
                for k in ('lowest_recorded_price','highest_recorded_price'):
                    try:
                        v=float(item.get(k))
                        if v>0: prices.append(v)
                    except: pass
                return {'found':True,'source':'UPCitemdb','title':item.get('title') or '',
                        'brand':item.get('brand') or '', 'model':item.get('model') or '',
                        'ean':item.get('ean') or item.get('gtin') or code,
                        'asin':item.get('asin') or '', 'category':item.get('category') or '',
                        'description':item.get('description') or '', 'images':item.get('images') or [],
                        'prices':prices[:20], 'offers':offers[:10]}
        return {'found':False,'source':'UPCitemdb','status':rr.status_code}
    except Exception as e:
        return {'found':False,'source':'UPCitemdb','error':str(e)}

def keepa_product(asin=None,code=None,domain=9):
 if not KEEPA_API_KEY:return {'enabled':False,'error':'Falta KEEPA_API_KEY'}
 p={'key':KEEPA_API_KEY,'domain':domain};
 if asin:p['asin']=asin
 elif code:p['code']=code
 try:
  d=requests.get('https://api.keepa.com/product',params=p,timeout=12).json(); x=(d.get('products') or [None])[0]
  if not x:return {'enabled':True,'error':d.get('error',{}).get('message','Producto no encontrado')}
  c=x.get('csv') or []; ap=cents(c[0][-1]) if len(c)>0 and c[0] else None; np=cents(c[1][-1]) if len(c)>1 and c[1] else None; bb=cents(x.get('buyBoxPrice')) or np or ap
  rank=c[3][-1] if len(c)>3 and c[3] and c[3][-1]>=0 else None
  return {'enabled':True,'asin':x.get('asin'),'title':x.get('title'),'brand':x.get('brand'),'amazon_price':ap,'new_price':np,'buy_box':bb,'sales_rank':rank,'rating':x.get('rating'),'review_count':x.get('reviewCount'),'tokens_left':d.get('tokensLeft')}
 except Exception as e:return {'enabled':True,'error':str(e)}
def keepa_search(q,domain):
 if not KEEPA_API_KEY or not q:return {}
 try:
  d=requests.get('https://api.keepa.com/search',params={'key':KEEPA_API_KEY,'domain':domain,'type':'product','term':q,'page':0},timeout=12).json()
  for av in (d.get('asinList') or [])[:5]:
   x=keepa_product(asin=av,domain=domain)
   if x.get('asin'):return x
 except:pass
 return {}
def market_lookup(mk,asin=None,code=None,q=''):
 flag,name,host,domain,currency=MARKETS[mk]; out={'market':mk,'flag':flag,'name':name,'host':host,'currency':currency,'keepa':bool(domain)}
 if not domain:
  out['message']='Este marketplace está incluido para comparación web; Keepa no expone actualmente un dominio API directo en esta integración.'
  out['search_url']=f'https://{host}/s?k='+requests.utils.quote(q or asin or code or '')
  return out
 x=keepa_product(asin=asin,code=code,domain=domain) if (asin or code) else keepa_search(q,domain)
 out.update(x); out['url']=f'https://{host}/dp/{x["asin"]}' if x.get('asin') else out.get('search_url')
 return out
def ebay_token():
 if not EBAY_CLIENT_ID or not EBAY_CLIENT_SECRET:return None
 try:return requests.post('https://api.ebay.com/identity/v1/oauth2/token',headers={'Content-Type':'application/x-www-form-urlencoded'},data={'grant_type':'client_credentials','scope':'https://api.ebay.com/oauth/api_scope'},auth=(EBAY_CLIENT_ID,EBAY_CLIENT_SECRET),timeout=10).json().get('access_token')
 except:return None
def ebay(q):
 t=ebay_token()
 if not t:return {'enabled':False,'items':[]}
 try:
  d=requests.get('https://api.ebay.com/buy/browse/v1/item_summary/search',params={'q':q,'limit':12,'sort':'price'},headers={'Authorization':f'Bearer {t}','X-EBAY-C-MARKETPLACE-ID':EBAY_MARKETPLACE_ID,'Accept-Language':'es-ES'},timeout=12).json(); out=[]
  for x in d.get('itemSummaries',[]):
   try:v=float(x.get('price',{}).get('value'))
   except:v=None
   if v is not None:out.append({'title':x.get('title'),'price':v,'url':x.get('itemWebUrl'),'condition':x.get('condition')})
  return {'enabled':True,'items':out}
 except Exception as e:return {'enabled':True,'items':[],'error':str(e)}
def identify(data_url):
 if not OPENAI_API_KEY:return {}
 q='Identifica este producto para arbitraje europeo. Devuelve SOLO JSON: {name,brand,model,ean_or_gtin,asin}. No inventes códigos.'
 try:
  r=requests.post('https://api.openai.com/v1/responses',headers={'Authorization':f'Bearer {OPENAI_API_KEY}','Content-Type':'application/json'},json={'model':OPENAI_MODEL,'input':[{'role':'user','content':[{'type':'input_text','text':q},{'type':'input_image','image_url':data_url}]}]},timeout=OPENAI_TIMEOUT).json(); m=re.search(r'\{.*\}',r.get('output_text',''),re.S); return json.loads(m.group()) if m else {}
 except Exception as e:return {'error':str(e)}


def google_lens_search(raw, content_type='image/jpeg'):
    """Búsqueda visual sin API oficial: sube la imagen a Google Lens y extrae candidatos públicos.
    Es un fallback web; Google puede cambiar este endpoint en cualquier momento.
    """
    try:
        headers={'User-Agent':'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/136 Mobile Safari/537.36','Accept-Language':'es-ES,es;q=0.9,en;q=0.8'}
        files={'encoded_image':('product.jpg',raw,content_type or 'image/jpeg')}
        data={'processed_image_dimensions':'1200,1200'}
        r=requests.post('https://lens.google.com/v3/upload?ep=ccm&s=&st=1',files=files,data=data,headers=headers,timeout=25,allow_redirects=False)
        loc=r.headers.get('location')
        if not loc:
            # Some deployments return the result HTML directly.
            loc=r.url if r.status_code in (200,302,303) else None
        if not loc:return {'enabled':True,'results':[],'error':'Google Lens no devolvió una URL de resultados'}
        rr=requests.get(loc,headers=headers,timeout=25,allow_redirects=True)
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(rr.text,'html.parser')
        results=[]; seen=set()
        # Extract useful result links/titles. Lens markup changes, so use several selectors.
        for a in soup.select('a'):
            href=a.get('href',''); title=a.get_text(' ',strip=True)
            if not href.startswith('http') or not title or len(title)<3: continue
            low=href.lower()
            if any(x in low for x in ('google.com','gstatic.com','googleusercontent.com')): continue
            key=(href,title)
            if key in seen: continue
            seen.add(key)
            results.append({'title':title[:240],'url':href})
            if len(results)>=25: break
        page_title=(soup.title.get_text(' ',strip=True) if soup.title else '')
        # Meta descriptions often contain Lens' detected object/category.
        meta=' '.join([(m.get('content') or '') for m in soup.select('meta[name="description"],meta[property="og:description"]')])
        return {'enabled':True,'results':results,'page_title':page_title,'description':meta[:500],'result_url':rr.url}
    except Exception as e:
        return {'enabled':True,'results':[],'error':str(e)}

def calc(cost,sale,comm,fixed,ship,tax,other):
 if sale is None:return None
 fees=sale*comm/100+fixed+ship+tax+other; profit=sale-cost-fees; return {'cost':eur(cost),'sale':eur(sale),'fees':eur(fees),'profit':eur(profit),'roi':eur(profit/cost*100 if cost else None),'margin':eur(profit/sale*100 if sale else None),'max_cost':eur(sale-fees)}
@app.get('/')
def home():return FileResponse(str(BASE_DIR/'index.html'))
@app.get('/manifest.webmanifest')
def manifest():
    return FileResponse(str(BASE_DIR/'manifest.webmanifest'), media_type='application/manifest+json')

@app.get('/sw.js')
def service_worker():
    return FileResponse(str(BASE_DIR/'sw.js'), media_type='application/javascript')

@app.get('/api/health')
def health():return {'openai':bool(OPENAI_API_KEY),'keepa':bool(KEEPA_API_KEY),'ebay':bool(EBAY_CLIENT_ID and EBAY_CLIENT_SECRET)}
@app.get('/api/config')
def config():
 return {'openai':bool(OPENAI_API_KEY),'keepa':bool(KEEPA_API_KEY),'ebay':bool(EBAY_CLIENT_ID and EBAY_CLIENT_SECRET),'web':True}

@app.post('/api/test-apis')
def test_apis():
 out={'openai':False,'keepa':False,'ebay':False,'errors':{}}
 if OPENAI_API_KEY:
  try:
   rr=requests.get('https://api.openai.com/v1/models',headers={'Authorization':f'Bearer {OPENAI_API_KEY}'},timeout=8)
   out['openai']=rr.ok
   if not rr.ok: out['errors']['OpenAI']=rr.text[:180]
  except Exception as e: out['errors']['OpenAI']=str(e)
 else: out['errors']['OpenAI']='OPENAI_API_KEY no configurada'
 if KEEPA_API_KEY:
  try:
   rr=requests.get('https://api.keepa.com/token',params={'key':KEEPA_API_KEY},timeout=8)
   out['keepa']=rr.ok and 'tokensLeft' in rr.text
   if not out['keepa']: out['errors']['Keepa']=rr.text[:180]
  except Exception as e: out['errors']['Keepa']=str(e)
 else: out['errors']['Keepa']='KEEPA_API_KEY no configurada'
 if EBAY_CLIENT_ID and EBAY_CLIENT_SECRET:
  t=ebay_token(); out['ebay']=bool(t)
  if not t: out['errors']['eBay']='No se pudo obtener el token'
 else: out['errors']['eBay']='Credenciales eBay no configuradas'
 return out


def clean_ocr_text(t):
    t=re.sub(r'\s+',' ',t or '').strip()
    # Remove common OCR noise while preserving model-like tokens.
    t=re.sub(r'[^\wÀ-ÿ.\-+/ ]',' ',t)
    return re.sub(r'\s+',' ',t).strip()[:500]

def extract_prices(text):
    vals=[]
    for m in re.finditer(r'(\d{1,4}(?:[.,]\d{1,2})?)\s*(?:€|EUR)', text or '', re.I):
        try:
            v=float(m.group(1).replace('.','').replace(',','.'))
            if 2 <= v <= 10000: vals.append(v)
        except: pass
    return vals

def smart_candidate_from_web(q):
    """Use public search results to refine OCR/manual text into a product name.
    No LLM/API is required. It is intentionally conservative: it only replaces
    a weak OCR label when several independent result titles share the same tokens.
    """
    q=clean_ocr_text(q)
    if not q:return {'title':'','results':[],'prices':[]}
    results=web_discover(q)
    toks=[x.lower() for x in re.findall(r'[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9+.-]{2,}',q)]
    bad={'producto','marca','modelo','nuevo','usado','segunda','mano','the','with','for','and'}
    toks=[x for x in toks if x not in bad]
    scored=[]
    for r in results:
        title=r.get('title','')
        low=title.lower()
        score=sum(1 for t in toks if t in low)
        prices=extract_prices(title+' '+r.get('snippet',''))
        scored.append((score,title,prices,r))
    scored.sort(key=lambda x:(x[0],len(x[2])),reverse=True)
    best_title=scored[0][1] if scored and scored[0][0]>=1 else q
    prices=[v for _,_,ps,_ in scored[:12] for v in ps]
    return {'title':best_title[:180], 'results':results[:15], 'prices':prices[:30]}

@app.post('/api/identify')
async def identify_endpoint(query:str=Form(''),asin:str=Form(''),ean:str=Form(''),image:Optional[UploadFile]=File(None)):
 # Manual identifiers work even without any API.
 base={'name':query.strip() or '', 'asin':get_asin(asin) or get_asin(query), 'ean':get_code(ean) or get_code(query), 'search_queries':[query.strip()] if query.strip() else []}
 if image and image.filename and OPENAI_API_KEY:
  raw=await image.read()
  p=identify('data:'+(image.content_type or 'image/jpeg')+';base64,'+base64.b64encode(raw).decode())
  if p.get('error'): return {'error':p['error']}
  base.update({'name':p.get('name') or p.get('model') or base['name'], 'brand':p.get('brand'), 'model':p.get('model'), 'asin':get_asin(p.get('asin','')) or base['asin'], 'ean':get_code(p.get('ean_or_gtin','')) or base['ean']})
 if not base['name'] and not base['asin'] and not base['ean'] and image and image.filename and not OPENAI_API_KEY:
  try:
   raw=await image.read()
   vis=google_lens_search(raw,image.content_type or 'image/jpeg')
   candidates=[]
   if vis.get('page_title'): candidates.append(vis['page_title'])
   candidates += [x.get('title','') for x in (vis.get('results') or []) if x.get('title')]
   # Pick the first useful non-Google result title as a candidate.
   for cand in candidates:
    cand=re.sub(r'Google Lens|Lens','',cand,flags=re.I).strip(' -|')
    if len(cand)>=4:
     base['name']=cand[:180]; base['visual_candidates']=vis.get('results',[])[:10]; break
  except Exception as e:
   base['visual_error']=str(e)
 if not base['name'] and not base['asin'] and not base['ean']:
  return {'error':'No he podido identificar el producto automáticamente. Prueba una foto más cercana o añade marca/modelo/EAN.'}
 base['title']=base['name'] or base['asin'] or ('EAN '+base['ean'] if base.get('ean') else '')
 # Barcode resolution is now DB-first, then web. The raw EAN must never be used as the product name.
 if base.get('ean'):
  try:
   db=upcitemdb_lookup(base['ean'])
   if db.get('found'):
    base['barcode_db']=db
    base.update({
      'name':db.get('title') or base.get('name'),
      'brand':db.get('brand') or base.get('brand'),
      'model':db.get('model') or base.get('model'),
      'asin':get_asin(db.get('asin','')) or base.get('asin'),
      'ean':get_code(db.get('ean','')) or base.get('ean')
    })
    base['title']=db.get('title') or base.get('title')
    base['db_prices']=db.get('prices') or []
   ean_queries=['EAN '+base['ean'], '"'+base['ean']+'"', base['ean']+' producto']
   if base.get('brand'): ean_queries.append(base['brand']+' '+base['ean'])
   if base.get('model'): ean_queries.append(base['model']+' '+base['ean'])
   ean_results=[]
   for eq in ean_queries:
    ean_results.extend(web_discover(eq))
    if len(ean_results)>=20: break
   seen=set(); unique=[]
   for rr in ean_results:
    if rr.get('url') not in seen: seen.add(rr.get('url')); unique.append(rr)
   if unique:
    base['web_candidates']=unique[:15]
    # Only replace the DB title when it is still empty/weak.
    if not base.get('title') or base.get('title')==base.get('ean'):
     for rr in unique:
      cand=(rr.get('title') or '').strip()
      low=cand.lower()
      if len(cand)>=6 and not any(x in low for x in ('google','bing','search','resultados','ean ')):
       base['title']=cand[:180]; break
    base['web_prices']=[v for rr in unique[:20] for v in extract_prices((rr.get('title') or '')+' '+(rr.get('snippet') or ''))][:40]
  except Exception as ex:
   base['barcode_error']=str(ex)
 # If we only have OCR/manual text, refine it against public web results.
 if base.get('name') and not base.get('brand') and not base.get('model') and not base.get('asin') and not base.get('ean'):
  try:
   smart=smart_candidate_from_web(base['name'])
   if smart.get('title'): base['title']=smart['title']; base['web_candidates']=smart['results']; base['web_prices']=smart['prices']
  except Exception: pass
 base['search_queries']=[x for x in [base['title'], base.get('brand'), base.get('model'), base.get('ean')] if x]
 return base

@app.post('/api/markets')
async def markets_endpoint(payload:dict):
 title=str(payload.get('title') or '')
 asin=get_asin(str(payload.get('asin') or ''))
 ean=get_code(str(payload.get('ean') or ''))
 selected=payload.get('markets') or list(MARKETS.keys())
 selected=[x for x in selected if x in MARKETS] or ['ES']
 rows=[]
 for mk in selected:
  x=market_lookup(mk,asin,ean,title)
  price=x.get('buy_box') or x.get('new_price') or x.get('amazon_price')
  x['price']=price
  rows.append(x)
 return {'markets':rows}

def web_discover(q):
 if not q:return []
 h={'User-Agent':'Mozilla/5.0 (Android 14; Mobile) AppleWebKit/537.36 Chrome/136 Mobile Safari/537.36','Accept-Language':'es-ES,es;q=0.9,en;q=0.8'}
 from bs4 import BeautifulSoup
 out=[]
 # Try several public search pages. Any one may be unavailable from a hosting provider.
 attempts=[
   ('https://www.google.com/search',{'q':q,'hl':'es'}),
   ('https://www.bing.com/search',{'q':q,'setlang':'es-ES'}),
   ('https://html.duckduckgo.com/html/',{'q':q})
 ]
 for url,params in attempts:
  try:
   rr=requests.get(url,params=params,headers=h,timeout=8)
   if not rr.ok: continue
   soup=BeautifulSoup(rr.text,'html.parser')
   selectors=['a.result__a','li.b_algo h2 a','div.MjjYud a']
   found=[]
   for sel in selectors:
    for a in soup.select(sel):
     href=a.get('href',''); title=a.get_text(' ',strip=True)
     if href.startswith('http') and title and len(title)>2:
      found.append({'title':title[:240],'url':href,'snippet':''})
   for x in found:
    if x['url'] not in {z['url'] for z in out}: out.append(x)
   if len(out)>=15: break
  except Exception:
   continue
 return out[:15]

def web_fallback_links(title):
 q=requests.utils.quote(title or '')
 return {
  'google':'https://www.google.com/search?q='+q,
  'bing':'https://www.bing.com/search?q='+q,
  'amazon_es':'https://www.amazon.es/s?k='+q,
  'ebay_es':'https://www.ebay.es/sch/i.html?_nkw='+q,
  'wallapop':'https://es.wallapop.com/app/search?keywords='+q,
  'google_lens':'https://lens.google.com/'
 }

@app.post('/api/visual-search')
async def visual_search(image:Optional[UploadFile]=File(None)):
 if not image or not image.filename:return {'error':'No se recibió ninguna imagen'}
 raw=await image.read()
 if len(raw)>6*1024*1024:return {'error':'La imagen es demasiado grande'}
 return google_lens_search(raw,image.content_type or 'image/jpeg')

@app.post('/api/discover')
async def discover(payload:dict):
 qs=payload.get('queries') or [payload.get('title') or '']
 out=[]
 for q in qs[:3]: out.extend(web_discover(str(q)))
 seen=set(); clean=[]
 for x in out:
  if x['url'] not in seen: seen.add(x['url']); clean.append(x)
 prices=[v for x in clean[:15] for v in extract_prices((x.get('title') or '')+' '+(x.get('snippet') or ''))]
 return {'results':clean[:15],'prices':prices[:30]}

@app.post('/api/analyze')
async def analyze(cost:float=Form(...),channel:str=Form('amazon'),commission:float=Form(15),fixed:float=Form(0),shipping:float=Form(0),tax:float=Form(0),other:float=Form(0),markets:str=Form('ES,DE,FR,IT,UK,NL,BE,PL,SE,IE'),query:str=Form(''),asin_in:str=Form(''),ean:str=Form(''),image:Optional[UploadFile]=File(None)):
 p={}
 if image and image.filename:
  raw=await image.read(); p=identify('data:'+(image.content_type or 'image/jpeg')+';base64,'+base64.b64encode(raw).decode())
 av=get_asin(asin_in) or get_asin(p.get('asin','')) or get_asin(query); code=get_code(ean) or get_code(p.get('ean_or_gtin','')); q=query or p.get('name') or p.get('model') or ''
 selected=[x for x in markets.split(',') if x in MARKETS] or ['ES']; rows=[market_lookup(m,av,code,q) for m in selected]
 es=next((x for x in rows if x['market']=='ES'),rows[0]); title=es.get('title') or p.get('name') or q or 'Producto'; e=ebay(title); vals=[x['price'] for x in e.get('items',[])]; med=statistics.median(vals) if vals else None
 candidates=[x for x in rows if x.get('currency')=='EUR' and (x.get('buy_box') or x.get('new_price') or x.get('amazon_price')) is not None]
 best=max(candidates,key=lambda x:x.get('buy_box') or x.get('new_price') or x.get('amazon_price')) if candidates else es
 sale=(best.get('buy_box') or best.get('new_price') or best.get('amazon_price')) if channel=='amazon' else med if channel=='ebay' else ((best.get('buy_box') or best.get('new_price') or best.get('amazon_price')) or med)
 c=calc(cost,sale,commission,fixed,shipping,tax,other); verdict='⚪ FALTAN DATOS' if not c else ('🟢 OPORTUNIDAD' if c['profit']>=10 and c['roi']>=30 else '🟡 ESTUDIAR' if c['profit']>0 and c['roi']>=15 else '🔴 NO COMPRAR')
 return {'product':p,'markets':rows,'best_market':best.get('market'),'ebay':e,'calculation':c,'verdict':verdict,'sale_source':best.get('name') if channel=='amazon' else 'eBay España','links':web_fallback_links(title),'notes':['Los mercados con dominio Keepa se consultan mediante Keepa.','Los demás mercados quedan preparados para búsqueda web directa.','El cálculo no sustituye las comisiones, impuestos, IVA/IGIC, logística o restricciones reales de tu cuenta de vendedor.']}
