import numpy as np, geopandas as gpd, pandas as pd, pathlib
from shapely.geometry import box
rng = np.random.default_rng(3)
comunas = [  # CUT, COMUNA, REGION, origen x,y (UTM19S)
 (5101,"VALPARAÍSO","VALPARAÍSO",255000,6340000),(5109,"VIÑA DEL MAR","VALPARAÍSO",262000,6345000),
 (5102,"CASABLANCA","VALPARAÍSO",275000,6320000),(5103,"CONCÓN","VALPARAÍSO",262000,6355000),
 (5105,"PUCHUNCAVÍ","VALPARAÍSO",265000,6370000),(5107,"QUINTERO","VALPARAÍSO",258000,6365000),
 (5501,"QUILLOTA","VALPARAÍSO",295000,6365000),(5502,"LA CALERA","VALPARAÍSO",300000,6375000),
 (5601,"SAN ANTONIO","VALPARAÍSO",255000,6280000),(5603,"CARTAGENA","VALPARAÍSO",258000,6290000),
 (13101,"SANTIAGO","METROPOLITANA DE SANTIAGO",345000,6297000),(13114,"LAS CONDES","METROPOLITANA DE SANTIAGO",355000,6302000),
 (13123,"PROVIDENCIA","METROPOLITANA DE SANTIAGO",350000,6300000),(13110,"LA FLORIDA","METROPOLITANA DE SANTIAGO",352000,6290000),
 (13119,"MAIPÚ","METROPOLITANA DE SANTIAGO",335000,6290000),(13105,"EL BOSQUE","METROPOLITANA DE SANTIAGO",343000,6283000),
 (13120,"ÑUÑOA","METROPOLITANA DE SANTIAGO",351000,6296000),(13201,"PUENTE ALTO","METROPOLITANA DE SANTIAGO",355000,6280000),
 (13202,"PIRQUE","METROPOLITANA DE SANTIAGO",358000,6272000),(13203,"SAN JOSÉ DE MAIPO","METROPOLITANA DE SANTIAGO",370000,6278000),
 (8101,"CONCEPCIÓN","BIOBÍO",675000,5920000),(8110,"TALCAHUANO","BIOBÍO",670000,5930000),
]
rows=[]
PROV={"051":"VALPARAÍSO","055":"QUILLOTA","056":"SAN ANTONIO","131":"SANTIAGO","132":"CORDILLERA","081":"CONCEPCIÓN"}
for cut,nom,reg,x0,y0 in comunas:
    b60=rng.uniform(12,28); besc=rng.uniform(9,16); bh=rng.uniform(3,15); n=int(rng.integers(8,16))
    for a in range(n):
        for b in range(n):
            x=x0+a*220; y=y0+b*260; p=int(rng.integers(0,400))
            m=int(rng.binomial(p,np.clip(b60+rng.normal(0,6),2,80)/100))
            vp=max(1,p//3); h=int(rng.binomial(vp,np.clip(bh+rng.normal(0,4),0,60)/100))
            if rng.random()<0.03: m=-99; h=-99
            e=rng.multinomial(p,[.08,.1,.06,.1,.3,.2,.16]); oc=int(p*.45); de=int(p*.04)
            rows.append(dict(CUT=cut,COMUNA=nom,COD_REGION=cut//1000,REGION=reg,PROVINCIA=PROV[str(cut).zfill(5)[:3]],
                AREA_C=1 if b>1 else 2, CONTENEDOR_COMUNAL=0,
                n_edad_0_5=e[0],n_edad_6_13=e[1],n_edad_14_17=e[2],n_edad_18_24=e[3],n_edad_25_44=e[4],n_edad_45_59=e[5],
                n_ocupado=oc,n_desocupado=de,n_fuera_fuerza_trabajo=max(0,int(p*.8)-oc-de),
                n_analfabet=int(rng.binomial(int(p*.8),np.clip(bh/4+rng.normal(0,1),0,30)/100)),
                n_hog=max(1,p//3),n_jefatura_mujer=int(rng.binomial(max(1,p//3),.45)),n_vp_ocupada=vp,
                n_per=p,n_edad_60_mas=m,
                prom_escolaridad18=float(np.clip(besc+rng.normal(0,1.5),4,20)) if rng.random()>0.02 else -99.0,
                n_vp=vp,n_viv_hacinadas=h,SHAPE=box(x,y,x+190,y+230)))
rows.append(dict(rows[0], CONTENEDOR_COMUNAL=1, n_per=50, n_edad_60_mas=10, SHAPE=box(250000,6330000,270000,6350000)))
g=gpd.GeoDataFrame(rows,geometry="SHAPE",crs=32719).to_crs(4326)
import shutil; shutil.rmtree("prueba_tarea/datos",ignore_errors=True)
d=pathlib.Path("prueba_tarea/datos/Cartografia_censo2024_Pais"); d.mkdir(parents=True,exist_ok=True)
g.to_parquet(d/"Cartografia_censo2024_Pais_Manzanas.parquet")
com=g.to_crs(32719).dissolve("CUT").reset_index()[["CUT","COMUNA","SHAPE"]]; com["SHAPE"]=com.buffer(400).buffer(-100)
com.to_crs(4326).to_parquet(d/"Cartografia_censo2024_Pais_Comunas.parquet")
import shutil; shutil.copy("/root/.claude/uploads/dd1361ea-bf01-5d3c-b1bd-5252284ba457/8c95c0d2-diccionario_variables_glosas_censo2024.xlsx", d/"diccionario_variables_glosas_censo2024.xlsx")
print(len(g))
