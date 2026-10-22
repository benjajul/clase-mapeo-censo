import numpy as np, geopandas as gpd, pathlib
from shapely.geometry import box
rng = np.random.default_rng(1)
nombres = ["SANTIAGO","CERRILLOS","CERRO NAVIA","CONCHALI","EL BOSQUE","ESTACION CENTRAL","HUECHURABA","INDEPENDENCIA",
 "LA CISTERNA","LA FLORIDA","LA GRANJA","LA PINTANA","LA REINA","LAS CONDES","LO BARNECHEA","LO ESPEJO","LO PRADO","MACUL",
 "MAIPU","NUNOA","PEDRO AGUIRRE CERDA","PENALOLEN","PROVIDENCIA","PUDAHUEL","QUILICURA","QUINTA NORMAL","RECOLETA","RENCA",
 "SAN JOAQUIN","SAN MIGUEL","SAN RAMON","VITACURA","PUENTE ALTO","SAN BERNARDO"]
cuts = [13100+i for i in range(1,33)] + [13201, 13401]
rows=[]; x0,y0 = 333000, 6277000
for i,(cut,nom) in enumerate(zip(cuts,nombres)):
    cx0 = x0 + (i % 6) * 4700; cy0 = y0 + (i // 6) * 5600
    b60 = rng.uniform(12, 26); besc = rng.uniform(10.5, 16.5); n_side = int(rng.integers(12, 20))
    for a in range(n_side):
        for b in range(n_side):
            x = cx0 + a*220; y = cy0 + b*270
            n = int(rng.integers(0, 400)); m = int(rng.binomial(n, np.clip(b60 + rng.normal(0,6),2,80)/100))
            esc = float(np.clip(besc + rng.normal(0,1.5), 4, 20))
            rows.append(dict(CUT=cut, COMUNA=nom, n_per=n, n_edad_60_mas=m, prom_escolaridad18=esc, SHAPE=box(x,y,x+190,y+240)))
g = gpd.GeoDataFrame(rows, geometry="SHAPE", crs=32719).to_crs(4326)
d=pathlib.Path("prueba/datos3/Cartografia_censo2024_Pais"); d.mkdir(parents=True, exist_ok=True)
g.to_parquet(d/"Cartografia_censo2024_Pais_Manzanas.parquet")
com = g.dissolve("CUT").reset_index()[["CUT","COMUNA","SHAPE"]]; com["SHAPE"]=com.buffer(0)
com.to_parquet(d/"Cartografia_censo2024_Pais_Comunas.parquet"); print(len(g))
