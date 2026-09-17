# -*- coding: utf-8 -*-
"""Generador del Dashboard Forecast (Electroestrada).
Uso: python generar_dashboard.py [ruta_xlsm] [salida_html]"""
import sys, os, json, glob, datetime, re
from datetime import timedelta
import openpyxl
from openpyxl.utils import column_index_from_string as ci

def _total(s):
    m=re.search(r'Total:\s*([\d\.]+)', s or "")
    return int(m.group(1).replace(".","")) if m else None
def _usd(s):
    s=s or ""
    def num(tag):
        m=re.search(tag+r'\s*:?\s*U\$D\s*([\d\.]+,\d{2}|[\d\.]+)', s)
        if not m: return None
        v=m.group(1).replace(".","").replace(",",".")
        try: return float(v)
        except: return None
    pi=num("PI"); cii=num("CI")
    if pi is None and cii is None:
        m=re.match(r'\s*([\d\.]+)\s*$', s)
        if m:
            try: pi=float(m.group(1))
            except: pass
    return [pi,cii]

def find_latest(folder):
    cands=[p for p in glob.glob(os.path.join(folder,"*.xlsm")) if not os.path.basename(p).startswith("~$")]
    if not cands: raise SystemExit("No se encontro ningun .xlsm en "+folder)
    return max(cands, key=os.path.getmtime)

def extract(path):
    wb=openpyxl.load_workbook(path, read_only=True, data_only=True, keep_links=False)
    ws=wb["Forecast"]
    BS=88; STRIDE=14
    all_rows=[list(x) for x in ws.iter_rows(min_row=1,max_row=6000,max_col=270,values_only=True)]
    _rl=all_rows[2] if len(all_rows)>2 else []
    real_labels=[(_rl[cc] if cc<len(_rl) else None) for cc in range(ci("AB")-1, ci("AB")-1+12)]
    r1=all_rows[0]
    months=[str(r1[BS+STRIDE*k]) for k in range(12)]
    def I(v):
        try: return int(round(float(v)))
        except: return None
    def F1(v):
        try: return round(float(v),1)
        except: return None
    def N(v):
        try: f=float(v)
        except: return None
        r=round(f,3)
        return int(r) if r==int(r) else r
    UN=[];GA=[];CAT=[]
    def idx(lst,v):
        v="" if v is None else str(v)
        if v not in lst: lst.append(v)
        return lst.index(v)
    rows=[]
    realmap={}
    for row in all_rows[3:]:
        cod=row[2]
        if not (cod and str(cod).strip()): continue
        # fila separadora del Excel: codigo "-", sin UN ni datos. Ensuciaba el
        # filtro de Categoria con un "-" que no existe como categoria.
        if str(cod).strip()=="-": continue
        if str(row[1]).strip()=="Adicionales": continue  # GA sin valor estadistico
        ui=idx(UN,row[0]); gi=idx(GA,row[1]); cti=idx(CAT,row[5])
        sa=N(row[ci("BN")-1]); ma=F1(row[ci("BO")-1])
        flat=[]; prev=ma
        for k in range(12):
            b=BS+STRIDE*k; bn=BS+STRIDE*(k+1)
            si=N(row[b+5-1]); mf=F1(row[b+7-1]); comp=N(row[b+10-1]); ven=N(row[b+1-1])
            ni=bn+5-1; sf=N(row[ni]) if ni<len(row) else None
            if sf is None and si is not None and comp is not None and ven is not None: sf=si+comp-ven
            flat += [si, prev, comp, ven, sf, mf]; prev=mf
        ideal=F1(row[ci("H")-1])
        cajax=N(row[ci("L")-1])
        # BV = "Venta ajustada": el ritmo mensual con el que el Excel calcula
        # "Meses actual" (BO = BN/BV). El dashboard lo necesita para que los meses
        # y las unidades hablen el mismo idioma en todas las solapas.
        vaj=N(row[ci("BV")-1])
        vpx=[]
        for k in range(12):
            b=BS+STRIDE*k
            vpx += [N(row[b+0-1]), N(row[b+4-1])]  # venta base, venta proy USD/$
        try: an=round(float(row[ci("AN")-1]),4)
        except: an=None
        try: pp=round(float(row[ci("AS")-1]),4)
        except: pp=None
        _rr=[]
        for cc in range(ci("AB")-1, ci("AB")-1+12):
            try: _rr.append(abs(float(row[cc])))
            except: _rr.append(None)
        realmap[str(cod).strip()]=_rr
        # Col G "Primer ingreso": cuando entro el codigo al catalogo. Va como numero
        # AAAAMMDD para que ordene solo; la plantilla lo muestra dd/mm/aa.
        _g=row[ci("G")-1]
        try: ing=int(_g.strftime("%Y%m%d"))
        except Exception: ing=None
        # una celda vacia puede venir como 01/01/1900: no es una fecha de ingreso
        if ing is not None and ing < 20000101: ing=None
        # Col CP "Stock maximo": la suma de la demanda de los proximos "Meses por
        # Cat." meses, cada uno con su estacionalidad. Arranca en el mes en curso
        # (busca la columna por el nombre del mes), a diferencia de CB que arranca
        # fija en AU. Es la base del maximo de Estado Stock.
        try: maxe=float(row[ci("CP")-1] or 0)
        except (TypeError,ValueError): maxe=0.0
        rows.append([ui,gi,str(cod).strip(),cti,sa,ma]+flat+[ideal]+vpx+[an]+[pp]+[cajax]+[vaj]+[ing]+[maxe])
    # IMPO por GA
    def estado_of(H1,b):
        for off in (8,9):
            v=H1[b-1+off]
            if v:
                u=str(v).upper()
                if "CONFIRM" in u: return "confirmado"
                if "PROYECT" in u: return "proyectado"
        return "-"
    heads=[]
    for i in range(3,len(all_rows)):
        row=all_rows[i]; b=row[1]; c=row[2]
        if (b and str(b).strip()) and not (c and str(c).strip()):
            heads.append((i,str(b).strip()))
    groups={}
    j=0
    while j<len(heads):
        gidx,ga=heads[j]; grp=[gidx]; k=j+1
        while k<len(heads) and heads[k][0]==heads[k-1][0]+1 and heads[k][1]==ga:
            grp.append(heads[k][0]); k+=1
        if ga not in groups: groups[ga]=grp
        j=k
    impo={}
    for ga,grp in groups.items():
        H1=all_rows[grp[0]]; H2=all_rows[grp[1]] if len(grp)>1 else H1
        arr=[]
        for kk in range(12):
            b=BS+STRIDE*kk
            num=H1[b-1+10]; fe=H1[b-1+12]
            disp=""; eta=""
            if hasattr(fe,"strftime"):
                disp=fe.strftime("%d/%m/%Y"); eta=(fe-timedelta(days=10)).strftime("%d/%m/%Y")
            elif fe: disp=str(fe)
            uc=_usd(str(H2[b-1+12] or "")); up=_usd(str(H2[b-1+9] or ""))
            arr.append({"mes":months[kk],"estado":estado_of(H1,b),
                "impo":(str(num).strip() if num else ""),
                "disp":disp,"eta":eta,
                "cant":_total(str(H2[b-1+10] or "")),"pi":uc[0],"ci":uc[1],
                "cant_proy":_total(str(H2[b-1+8] or "")),"pi_proy":up[0],"ci_proy":up[1]})
        impo[ga]=arr
    # ---- Estacionalidad / Evento especial / TC por mes ----
    # Estac. y Evento se leen DIRECTO de la hoja "Estacionalidad" (lo que edita el usuario),
    # con 2 decimales para no perder los pasos de 5% (0.95, 1.05). No dependen del cache
    # de la fórmula XLOOKUP, así siempre reflejan el valor actual sin recalcular.
    def P2(v):
        try: return round(float(v),2)
        except: return None
    _estac={}
    try:
        _essheet=None
        for _sn in wb.sheetnames:
            if _sn.strip().lower().replace("ó","o")=="configuracion": _essheet=wb[_sn]; break
        if _essheet is None:
            raise Exception("no hay hoja 'Configuracion'. Hojas disponibles: "+", ".join(wb.sheetnames))
        for _r in _essheet.iter_rows(min_row=1, max_col=14, values_only=True):
            mn=_r[ci("L")-1] if len(_r)>ci("L")-1 else None
            es=_r[ci("M")-1] if len(_r)>ci("M")-1 else None
            ev=_r[ci("N")-1] if len(_r)>ci("N")-1 else None
            if isinstance(mn, str) and isinstance(es, (int, float)):
                _estac[mn.strip().lower()] = (P2(es), P2(ev))
        print("  Estacionalidad: %d meses leidos de 'Configuracion' (cols L/M/N)"%len(_estac))
    except Exception as _e:
        print("  Estacionalidad: uso valores cacheados del bloque (2 dec):", _e)
    season=[]
    for k in range(12):
        b=BS+STRIDE*k
        def r2(off): return all_rows[1][b+off-1]
        _mn=str(months[k]).strip().lower()
        if _mn in _estac:
            _es_v,_ev_v=_estac[_mn]
        else:
            _es_v,_ev_v=P2(r2(9)),P2(r2(12))  # fallback al cache de la fórmula (2 dec)
        season.append([_es_v, _ev_v, F1(r2(4))])  # estac, evento, TC
    # fecha/hora del stock (BN2 + BO2)
    bn=all_rows[1][ci("BN")-1]; bo=all_rows[1][ci("BO")-1]
    dias=["Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"]
    mes_es=["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    if hasattr(bn,"strftime"):
        ts="%s %02d de %s %d"%(dias[bn.weekday()],bn.day,mes_es[bn.month-1],bn.year)
    else: ts=str(bn or "")
    hora=""
    if bo:
        mm=re.search(r"(\d{1,2}:\d{2})",str(bo)); hora=mm.group(1) if mm else ""
    stock_ts=ts+(" / "+hora+" hs" if hora else "")
    # La misma fecha en formato comparable: el stock_ts es para mostrar y no se puede
    # ordenar ("Martes 15 de Septiembre"). Esta se usa para saber si la foto del stock
    # es nueva respecto de la corrida anterior (ver aplicar_memoria).
    stock_iso=(bn.strftime("%Y-%m-%d")+((" "+hora) if hora else "")) if hasattr(bn,"strftime") else ""
    return {"months":months,"UN":UN,"GA":GA,"CAT":CAT,"rows":rows,"impo":impo,"stock_ts":stock_ts,
            "stock_iso":stock_iso,"season":season,
            "real":realmap,"real_labels":real_labels,
            "src":os.path.basename(path),"gen":datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}

COSTOS_LOCAL = 'costos_gestor.xlsx'   # copia del Google Sheet, al lado de este script

def load_costos(path):
    """Costos y CMM del Gestor de precios.

    Fuente: Google Sheet 'Gestor de precios - DATOS', hoja 'General'.
    Encabezados en la fila 1, datos desde la fila 2:

        B = Codigo | F = CMM % | H = Moneda | I = Lista vigente | M = Costo

    El Sheet es privado, asi que no se puede bajar desde un script suelto: lo baja
    Claude desde el chat (conector de Google Drive) y deja la copia en
    scripts/costos_gestor.xlsx. Esa copia es la que se lee aca.

    Reemplaza al viejo Costos.xlsm, obsoleto desde el 14/09/2026.

    Devuelve {codigo: [costo, lista, cmm, moneda]}. El CMM viene del Gestor: el
    dashboard ya no lo calcula (ver computeLiq en plantilla.html)."""
    try:
        if not os.path.exists(path):
            print('  Costos: NO existe la copia del Gestor en:', path)
            print('          Pedile a Claude que baje la planilla de nuevo.')
            return {}
        wb=openpyxl.load_workbook(path, read_only=True, data_only=True, keep_links=False)
        gs=None
        for sn in wb.sheetnames:
            if sn.strip().lower()=='general': gs=wb[sn]; break
        if gs is None:
            print('  Costos: no hay hoja General. Hojas:', ', '.join(wb.sheetnames)); return {}
        d={}
        def nf(x):
            try: return round(float(x),4)
            except: return None
        for r in gs.iter_rows(min_row=2, max_row=8000, max_col=16, values_only=True):
            cod=r[1]
            if cod and str(cod).strip():
                cur=r[ci('H')-1]; cur='USD' if (cur and 'USD' in str(cur).upper()) else '$'
                d[str(cod).strip()]=[nf(r[ci('M')-1]), nf(r[ci('I')-1]), nf(r[ci('F')-1]), cur]
        if not d:
            print('  Costos: la hoja %s se leyo pero 0 codigos (codigo en col B, datos desde fila 2?)'%gs.title)
        else:
            import datetime as _dt
            _m=_dt.datetime.fromtimestamp(os.path.getmtime(path))
            print('  Costos: Gestor de precios -> %d codigos (copia del %s)'%(len(d), _m.strftime('%d/%m/%Y %H:%M')))
        return d
    except Exception as e:
        print('  Costos: error leyendo la copia del Gestor:', e); return {}

_MES={'ene':1,'feb':2,'mar':3,'abr':4,'may':5,'jun':6,'jul':7,'ago':8,'sep':9,'sept':9,'oct':10,'nov':11,'dic':12}
def _parse_label(s):
    if isinstance(s,(datetime.datetime, datetime.date)): return (s.year, s.month)
    s=str(s or "").strip().lower().replace('.','')
    m=re.match(r'([a-zñ]+)\s*[-_/ ]\s*(\d{2,4})', s)
    if not m: return None
    tok=m.group(1); mo=_MES.get(tok[:4]) or _MES.get(tok[:3])
    if not mo: return None
    y=int(m.group(2)); y=2000+y if y<100 else y
    return (y,mo)
def _parse_fname(fn):
    m=re.search(r'forecast\s+(\d{1,2})\s*[-_ ]\s*(\d{2,4})', fn.lower())
    if not m: return None
    mo=int(m.group(1)); y=int(m.group(2)); y=2000+y if y<100 else y
    return (y,mo)
_MESF={'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,'julio':7,'agosto':8,'septiembre':9,'setiembre':9,'octubre':10,'noviembre':11,'diciembre':12}
def _month_of(val):
    if isinstance(val,(datetime.datetime,datetime.date)): return val.month
    s=str(val or "").strip().lower().replace('.','')
    if not s: return None
    if s in _MESF: return _MESF[s]
    for name,mo in _MESF.items():
        if s.startswith(name[:4]): return mo
    pr=_parse_label(s)
    return pr[1] if pr else None
def extract_vp_archive(path, month):
    wb=openpyxl.load_workbook(path, read_only=True, data_only=True, keep_links=False)
    ws=wb["Forecast"]
    rr=[list(x) for x in ws.iter_rows(min_row=1, max_row=6000, max_col=200, values_only=True)]
    r1=rr[0] if rr else []; r2=rr[1] if len(rr)>1 else []; r3=rr[2] if len(rr)>2 else []
    targets=[]
    for hdr in (r1,r2):
        for cix,val in enumerate(hdr):
            if _month_of(val)==month: targets.append(cix)
    targets=sorted(set(targets))
    vpcol=None
    for t in targets:
        for cix in range(t, min(t+16,len(r3))):
            h=str(r3[cix] or "").lower()
            if ("venta proy" in h) and ("unidad" in h): vpcol=cix; break
        if vpcol is not None: break
    if vpcol is None: return {}
    mixcol=None
    for hdr in (r1,r2,r3):
        for cix,val in enumerate(hdr):
            if str(val or "").strip().upper()=="MIX": mixcol=cix; break
        if mixcol is not None: break
    d={}
    for row in rr[5:]:
        cod=row[2] if len(row)>2 else None
        if not (cod and str(cod).strip()): continue
        try:
            v=float(row[vpcol]); v=round(v,3); v=int(v) if v==int(v) else v
        except: v=None
        mx=None
        if mixcol is not None:
            try: mx=round(float(row[mixcol]),4)
            except: mx=None
        d[str(cod).strip()]=[v,mx]
    return d
def _parse_realusd_rows(rr, origen):
    r1=rr[0] if rr else []; r2=rr[1] if len(rr)>1 else []
    # cada mes tiene 3 columnas: Cant / Pesos / Dólares
    col_c={}; col_p={}; col_d={}; cur=None
    for c in range(len(r1)):
        mo=_month_of(r1[c]) if r1[c] else None
        if mo: cur=mo
        sub=str((r2[c] if c<len(r2) else "") or "").strip().lower()
        sub=sub.replace("ó","o").replace("á","a").replace("é","e").replace("í","i").replace("ú","u")
        if cur:
            if "cant" in sub or "unid" in sub: col_c[cur]=c
            elif "peso" in sub: col_p[cur]=c
            elif ("dolar" in sub or "usd" in sub or "u$" in sub): col_d[cur]=c
    codcol=1
    for c in range(len(r1)):
        if "digo" in str(r1[c] or "").lower(): codcol=c; break
    allmo=sorted(set(list(col_c)+list(col_p)+list(col_d)))
    d={}
    for row in rr[2:]:
        cod=row[codcol] if codcol<len(row) else None
        if not (cod and str(cod).strip()) or str(cod).strip().upper()=="TOTAL": continue
        def _f(col):
            try: return float(row[col])
            except: return None
        m={}
        for mo in allmo:
            cant=_f(col_c[mo]) if mo in col_c else None
            pesos=_f(col_p[mo]) if mo in col_p else None
            dol=_f(col_d[mo]) if mo in col_d else None
            if cant is not None: cant=abs(cant)
            if cant is not None or pesos is not None or dol is not None:
                m[mo]=[cant,pesos,dol]  # [unidades, pesos, dolares]
        if m: d[str(cod).strip()]=m
    print("  Venta real: %s -> %d codigos, meses %s (cant/pesos/dolares)"%(origen,len(d),allmo))
    return d

def read_realusd(forecast_path):
    """Venta real: SIEMPRE de la hoja "V.R. mensual" del propio Forecast.xlsm.

    Sin respaldo a un archivo suelto (decision de Erik, 14/09/2026): un archivo viejo
    olvidado en la carpeta pisaba el dato bueno sin que se notara. Si la hoja no esta,
    se corta la generacion en vez de publicar un Historico sin venta real."""
    if not (forecast_path and os.path.exists(forecast_path)):
        raise SystemExit("ERROR: no se encontro el Forecast.xlsm para leer la venta real.")
    wb=openpyxl.load_workbook(forecast_path, read_only=True, data_only=True, keep_links=False)
    hoja=None
    for sn in wb.sheetnames:
        nn=sn.strip().lower().replace(".","").replace(" ","")
        if nn in ("vrmensual","ventareal","vr"):
            hoja=wb[sn]; break
    if hoja is None:
        msg = ("""
ERROR: el Forecast.xlsm no tiene la hoja 'V.R. mensual'.
       Hojas encontradas: {hojas}
       Sin esa hoja el Historico queda sin venta real, asi que no se genera
       el dashboard. Revisa el nombre de la hoja en el Excel.""")
        raise SystemExit(msg.format(hojas=', '.join(wb.sheetnames)))
    rr=[list(x) for x in hoja.iter_rows(min_row=1,max_row=8000,max_col=40,values_only=True)]
    return _parse_realusd_rows(rr, "hoja '%s' de %s"%(hoja.title, os.path.basename(forecast_path)))

def build_historico(folder, real_map, real_labels, cache_path, realusd, imp_cods=None):
    imp_cods=imp_cods or set()
    cache={}
    if os.path.exists(cache_path):
        try: cache=json.load(open(cache_path,encoding="utf-8"))
        except: cache={}
    _bases=[os.path.join(folder,"Histórico"), os.path.join(folder,"Historico")]
    _cand=[]
    for _b in _bases:
        _cand += glob.glob(os.path.join(_b,"Forecast *"))
    for pth in _cand:
        bn=os.path.basename(pth)
        if bn.startswith("~$"): continue
        if not bn.lower().endswith((".xlsx",".xlsm")): continue
        pr=_parse_fname(bn)
        if not pr: continue
        key="%04d-%02d"%pr
        if key in cache: continue
        print("  Historico: leyendo",bn,"(una sola vez, puede tardar)...")
        try: cache[key]=extract_vp_archive(pth, pr[1])
        except Exception as e: print("    error:",e); continue
    try: json.dump(cache, open(cache_path,"w",encoding="utf-8"), ensure_ascii=False, separators=(",",":"))
    except Exception: pass
    _MN=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
    lab2={}
    for i,lab in enumerate(real_labels):
        pr=_parse_label(lab)
        if pr: lab2["%04d-%02d"%pr]=(i,"%s %d"%(_MN[pr[1]-1], pr[0]))
    keys=sorted(k for k in cache.keys() if k in lab2)
    months=[{"key":k,"label":lab2[k][1]} for k in keys]
    cods=set()
    for k in keys: cods|=set(cache[k].keys())
    cods|=set(real_map.keys()); cods|=set(realusd.keys())
    vpm={}; realm={}; mixm={}; reald={}
    for cod in cods:
        vr=[]; rr=[]; mm=[]; rd=[]; any_=False
        for k in keys:
            ent=cache[k].get(cod)
            vv=ent[0] if isinstance(ent,list) else ent
            mx=ent[1] if (isinstance(ent,list) and len(ent)>1) else None
            vr.append(vv); mm.append(mx)
            mo=int(k[5:7]); _ru=realusd.get(cod,{}).get(mo)
            if isinstance(_ru,list):
                run=_ru[0] if len(_ru)>0 else None   # V.R. u (unidades)
                # V.R. $-USD: Dolares si es importado, Pesos si no (misma logica de moneda del dashboard)
                rud=(_ru[2] if len(_ru)>2 else None) if (cod in imp_cods) else (_ru[1] if len(_ru)>1 else None)
            else:
                run=None; rud=_ru
            rr.append(run); rd.append(rud)
            if vv is not None or run is not None or rud is not None: any_=True
        if any_: vpm[cod]=vr; realm[cod]=rr; mixm[cod]=mm; reald[cod]=rd
    return {"months":months,"vp":vpm,"real":realm,"mix":mixm,"reald":reald}

# --------------------------------------------------------------------------------
# Memoria del mes: el dashboard anterior ES la foto anterior del stock.
#
# stock hoy = stock inicio + lo que entro - lo que se vendio. Son dos incognitas y una
# sola ecuacion, asi que con una foto sola no se puede saber cuanto se vendio en el mes
# en curso: si un codigo va 0 -> 1 -> 0, la venta desaparece. Y el Excel no lo publica
# (V.R. mensual llega hasta el mes cerrado anterior).
#
# La foto anterior ya existe: es el propio Dashboard_Forecast.html que estamos por
# pisar. Asi que el generador se lee a si mismo, suma lo que BAJO desde la corrida
# anterior y lo guarda en el HTML nuevo. No hace falta saber por que subio el stock
# -- nota de credito, devolucion de cliente, correccion de stock --: solo se cuentan
# las bajas, que es lo unico que es venta.
#
# No agrega ningun archivo al circuito y no se puede desincronizar: si el HTML no esta,
# arranca de cero y el dashboard se comporta como antes.
VACU = 109   # venta acumulada del mes; ultimo campo de cada fila de rows[]

def leer_anterior(path):
    """(mes, stock_iso, {cod: [stock, acumulado]}) del HTML anterior, o None."""
    if not os.path.exists(path): return None
    try:
        s=open(path,encoding="utf-8").read()
        i=s.index("const DATA =")+len("const DATA =")
        prev=json.loads(s[i:s.index("\n",i)].rstrip().rstrip(";"))
    except Exception as e:
        print("  Memoria: no se pudo leer el dashboard anterior (%s)"%e); return None
    iso=prev.get("stock_iso") or ""
    d={}
    for r in prev.get("rows",[]):
        if len(r)>4: d[r[2]]=[r[4] or 0, (r[VACU] if len(r)>VACU else 0) or 0]
    return (iso[:7], iso, d)

def aplicar_memoria(data, out_html):
    ant=leer_anterior(out_html)
    mes=(data.get("stock_iso") or "")[:7]
    if not ant or ant[0]!=mes:
        # mes nuevo, o no hay dashboard anterior: se empieza a contar desde aca
        for r in data["rows"]: r.append(0)
        print("  Memoria: arranca de cero (mes nuevo o sin dashboard anterior)")
        return
    _,iso_ant,d=ant
    if iso_ant>=(data.get("stock_iso") or ""):
        # el mismo Excel, o uno mas viejo: no hay foto nueva, no se inventa nada
        for r in data["rows"]: r.append(d.get(r[2],[None,0])[1])
        print("  Memoria: sin foto nueva (anterior %s), se arrastra lo acumulado"%iso_ant)
        return
    nuevas=0; tocados=0
    for r in data["rows"]:
        st,ac=d.get(r[2],[None,0])
        baja=max(0,(st or 0)-(r[4] or 0)) if st is not None else 0
        if baja: nuevas+=baja; tocados+=1
        r.append(ac+baja)
    print("  Memoria: %s -> %s | %d unidades en %d codigos"
          %(iso_ant,data["stock_iso"],nuevas,tocados))

def build(data, out_html, tpl_path):
    tpl=open(tpl_path,encoding="utf-8").read()
    html=tpl.replace("/*__DATA__*/", json.dumps(data,ensure_ascii=False,separators=(",",":")))
    open(out_html,"w",encoding="utf-8").write(html)
    print("OK ->",out_html, round(os.path.getsize(out_html)/1024),"KB | codigos:",len(data["rows"]),"| GA con IMPO:",len(data["impo"]))

if __name__=="__main__":
    folder=os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv)>1 else find_latest(folder)
    out = sys.argv[2] if len(sys.argv)>2 else os.path.join(folder,"index.html")
    # 5to argumento opcional: otra plantilla, para generar previews sin tocar la real
    tpl = sys.argv[4] if len(sys.argv)>4 else os.path.join(folder,"plantilla.html")
    print("Leyendo:",src)
    data=extract(src)
    cp = sys.argv[3] if len(sys.argv)>3 else os.path.join(folder, COSTOS_LOCAL)
    data["costos"]=load_costos(cp)
    try:
        imp_cods={data["rows"][i][2] for i in range(len(data["rows"])) if data["UN"][data["rows"][i][0]]=="Importados"}
        hist=build_historico(os.path.dirname(os.path.abspath(src)), data.get("real",{}), data.get("real_labels",[]), os.path.join(folder,"historico_vp.json"), read_realusd(os.path.abspath(src)), imp_cods)
        data["hist"]=hist
        print("Historico: meses",len(hist["months"]),"| codigos",len(hist["vp"]))
    except Exception as e:
        print("Historico: error",e); data["hist"]={"months":[],"vp":{},"real":{}}
    data.pop("real",None); data.pop("real_labels",None)
    aplicar_memoria(data, out)
    build(data, out, tpl)
