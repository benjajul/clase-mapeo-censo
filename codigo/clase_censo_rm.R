# =============================================================================
# Mapeo de variables censales en la Región Metropolitana
# ¿Dónde se concentran las personas mayores (60 años y más) en la RM?
#
# Versión en R para RStudio: OPCIONAL y de referencia (la clase se trabaja en Google Colab).
# Homologada bloque a bloque con el notebook de Python.
# Datos: INE, Censo de Población y Vivienda 2024 — Cartografía País (GeoParquet).
# Ejecuta los bloques en orden. Solo debes editar el Bloque 2.
# Si las tildes se ven mal: File > Reopen with Encoding > UTF-8.
# En RStudio, usa el panel "Outline" (Ctrl+Shift+O) para navegar entre bloques.
# =============================================================================


# Bloque 0 · Instalación de librerías -----------------------------------------
# Ejecutar solo una vez por computador (quita el # de la línea siguiente):
# install.packages(c("arrow", "sf", "dplyr", "ggplot2", "ggspatial", "prettymapr",
#                    "leaflet", "htmlwidgets", "classInt", "jsonlite", "zip"))


# Bloque 1 · Cargar librerías -------------------------------------------------
library(arrow)       # leer Parquet / GeoParquet
library(sf)          # datos espaciales (simple features)
library(dplyr)       # manipulación de tablas
library(ggplot2)     # gráficos y mapas estáticos
library(ggspatial)   # mapa base OSM, escala y norte para ggplot
library(leaflet)     # mapas web interactivos
library(htmlwidgets) # guardar el mapa web como HTML
library(classInt)    # clasificación de valores (cuantiles, etc.)


# Bloque 2 · Definir rutas y parámetros (EDITAR) -------------------------------
RUTA_MANZANAS <- "C:/Users/TU_USUARIO/Descargas/Cartografia_censo2024_Pais/Cartografia_censo2024_Pais_Manzanas.parquet"
RUTA_COMUNAS  <- NULL   # opcional: ruta a Cartografia_censo2024_Pais_Comunas.parquet

CARPETA_SALIDA <- "resultados"
dir.create(CARPETA_SALIDA, showWarnings = FALSE)

COL_CUT     <- "CUT"                 # código comunal (5 dígitos)
COL_COMUNA  <- "COMUNA"
COL_POB     <- "n_per"               # total de personas
COL_MAYORES <- "n_edad_60_mas"       # personas de 60 años y más
COL_ESCOLAR <- "prom_escolaridad18"  # escolaridad promedio (18+)

CODIGO_REGION <- "13"   # Región Metropolitana
MIN_PERSONAS  <- 20     # mínimo de personas para calcular tasas por manzana
CRS_METROS    <- 32719  # WGS 84 / UTM zona 19S


# Bloque 3 · Explorar el archivo antes de cargarlo -----------------------------
esquema  <- open_dataset(RUTA_MANZANAS)$schema
geo_meta <- jsonlite::fromJSON(esquema$metadata$geo, simplifyVector = FALSE)
COL_GEOM <- geo_meta$primary_column
cat("Columnas:", length(esquema$names), "| geometría:", COL_GEOM, "\n")
print(grep("edad", esquema$names, value = TRUE, ignore.case = TRUE))


# Bloque 4 · Cargar solo las columnas necesarias -------------------------------
leer_geoparquet <- function(ruta, columnas = NULL) {
  esq  <- open_dataset(ruta)$schema
  meta <- jsonlite::fromJSON(esq$metadata$geo, simplifyVector = FALSE)
  geom <- meta$primary_column
  crs_json <- meta$columns[[geom]]$crs
  crs <- if (is.null(crs_json)) st_crs(4326) else
    st_crs(jsonlite::toJSON(crs_json, auto_unbox = TRUE, digits = NA))
  tabla <- read_parquet(ruta, col_select = all_of(unique(c(columnas, geom))))
  tabla <- as.data.frame(tabla)
  tabla$geometry <- st_as_sfc(structure(as.list(tabla[[geom]]), class = "WKB"), crs = crs)
  tabla[[geom]] <- NULL
  st_as_sf(tabla, sf_column_name = "geometry")
}

manzanas <- leer_geoparquet(RUTA_MANZANAS, c(COL_CUT, COL_COMUNA, COL_POB, COL_MAYORES, COL_ESCOLAR))
print(dim(manzanas))
head(manzanas)


# Bloque 5 · Filtrar la Región Metropolitana -----------------------------------
# Los códigos se tratan como texto para no perder ceros iniciales (ej. 05101)
manzanas[[COL_CUT]] <- sprintf("%05d", as.integer(manzanas[[COL_CUT]]))
rm_mz <- manzanas[startsWith(manzanas[[COL_CUT]], CODIGO_REGION), ]
rm(manzanas); invisible(gc())
cat("Manzanas en la RM:", nrow(rm_mz), "| Comunas:", length(unique(rm_mz[[COL_CUT]])), "\n")


# Bloque 6 · Revisar el sistema de coordenadas ---------------------------------
print(st_crs(rm_mz)$Name)
sf_use_s2(FALSE)
rm_mz <- st_transform(rm_mz, CRS_METROS)
rm_mz$area_km2 <- as.numeric(st_area(rm_mz)) / 1e6
summary(rm_mz$area_km2)


# Bloque 7 · Limpiar los datos -------------------------------------------------
for (col in c(COL_POB, COL_MAYORES, COL_ESCOLAR)) {
  x <- suppressWarnings(as.numeric(rm_mz[[col]]))
  x[!is.na(x) & x < 0] <- NA            # valores suprimidos/negativos → faltantes
  rm_mz[[col]] <- x
}
rm_mz$valida <- !is.na(rm_mz[[COL_POB]]) & rm_mz[[COL_POB]] >= MIN_PERSONAS
cat("Manzanas válidas:", sum(rm_mz$valida), "de", nrow(rm_mz), "\n")


# Bloque 8 · Calcular el indicador por manzana ---------------------------------
rm_mz$pct_60 <- ifelse(rm_mz$valida, rm_mz[[COL_MAYORES]] / rm_mz[[COL_POB]] * 100, NA)
summary(rm_mz$pct_60)


# Bloque 9 · Agregar a nivel comunal -------------------------------------------
tabla <- rm_mz |>
  st_drop_geometry() |>
  mutate(escol_x_pob = .data[[COL_ESCOLAR]] * .data[[COL_POB]],
         pob_escol   = ifelse(is.na(.data[[COL_ESCOLAR]]), NA, .data[[COL_POB]])) |>
  group_by(cut = .data[[COL_CUT]], comuna = .data[[COL_COMUNA]]) |>
  summarise(poblacion = sum(.data[[COL_POB]], na.rm = TRUE),
            mayores   = sum(.data[[COL_MAYORES]], na.rm = TRUE),
            escolar   = sum(escol_x_pob, na.rm = TRUE) / sum(pob_escol, na.rm = TRUE),
            .groups = "drop") |>
  mutate(pct_60 = mayores / poblacion * 100)

if (!is.null(RUTA_COMUNAS)) {
  capa <- leer_geoparquet(RUTA_COMUNAS) |> st_transform(CRS_METROS)
  col_cut_capa <- names(capa)[toupper(names(capa)) %in% c("CUT", "COD_COMUNA", "CODIGO_COMUNA")][1]
  comunas <- capa |> transmute(cut = sprintf("%05d", as.integer(.data[[col_cut_capa]])))
} else {
  comunas <- rm_mz |> group_by(cut = .data[[COL_CUT]]) |> summarise(.groups = "drop")
}

comunas <- comunas |>
  inner_join(tabla, by = "cut") |>
  mutate(densidad = poblacion / (as.numeric(st_area(geometry)) / 1e6)) |>
  st_simplify(dTolerance = 25)

comunas |> st_drop_geometry() |> arrange(desc(pct_60)) |> head(10)


# Bloque 10 · Gráfico: envejecimiento y escolaridad por comuna -----------------
promedio_rm <- sum(comunas$mayores) / sum(comunas$poblacion) * 100
extremos <- bind_rows(slice_max(comunas, pct_60, n = 5), slice_min(comunas, pct_60, n = 5))

g <- ggplot(comunas, aes(escolar, pct_60)) +
  geom_hline(yintercept = promedio_rm, linetype = "dashed", colour = "grey50") +
  geom_point(aes(size = poblacion), colour = "#c2410c", alpha = 0.6) +
  geom_text(data = extremos, aes(label = tools::toTitleCase(tolower(comuna))),
            hjust = -0.1, vjust = -0.4, size = 3) +
  scale_size_area(max_size = 12, guide = "none") +
  labs(title = "Comunas de la RM: envejecimiento y escolaridad",
       x = "Años de escolaridad promedio (personas de 18 años y más)",
       y = "Personas de 60 años y más (%)",
       caption = sprintf("Fuente: INE, Censo 2024. Línea: promedio RM (%.1f%%). Tamaño = población.", promedio_rm)) +
  theme_minimal(base_size = 11) +
  theme(plot.title = element_text(face = "bold"))
print(g)
ggsave(file.path(CARPETA_SALIDA, "grafico_envejecimiento_escolaridad.png"), g, width = 9, height = 6, dpi = 200)


# Bloque 11 · Mismo dato, distinto mapa: métodos de clasificación --------------
clasificar <- function(x, metodo, k = 5) {
  cortes <- classIntervals(x, n = k, style = metodo)$brks
  cut(x, breaks = unique(cortes), include.lowest = TRUE, dig.lab = 3)
}
comparacion <- bind_rows(
  comunas |> mutate(clase = clasificar(pct_60, "quantile"), metodo = "Cuantiles"),
  comunas |> mutate(clase = clasificar(pct_60, "equal"),    metodo = "Intervalos iguales"))

ggplot(comparacion) +
  geom_sf(aes(fill = clase), colour = "white", linewidth = 0.2) +
  scale_fill_brewer(palette = "YlOrRd", name = "% 60+") +
  facet_wrap(~metodo) +
  labs(title = "¿Cuál de los dos mapas 'dice la verdad'?") +
  theme_void()


# Bloque 12 · Mapa interactivo sobre OpenStreetMap (HTML) ----------------------
comunas_wgs <- st_transform(comunas, 4326)
paleta <- colorQuantile("YlOrRd", comunas_wgs$pct_60, n = 5)

mapa_web <- leaflet(comunas_wgs) |>
  addTiles() |>                                   # OpenStreetMap
  addPolygons(fillColor = ~paleta(pct_60), fillOpacity = 0.75, color = "white", weight = 0.6,
              label = ~sprintf("%s: %.1f%% de 60+", comuna, pct_60)) |>
  addLegend(pal = paleta, values = ~pct_60, title = "% 60+ (quintiles)")
mapa_web
saveWidget(mapa_web, file.path(normalizePath(CARPETA_SALIDA), "mapa_interactivo_60mas.html"), selfcontained = TRUE)


# Bloque 13-14 · Mapa profesional por manzana (PNG / JPG) ----------------------
TITULO <- "¿Dónde viven las personas mayores en el Gran Santiago?"   # reemplazar por el hallazgo
gran_santiago <- st_bbox(st_transform(st_as_sfc(st_bbox(c(xmin = -70.85, ymin = -33.65, xmax = -70.45, ymax = -33.30), crs = 4326)), CRS_METROS))

validas <- rm_mz[rm_mz$valida, ]
validas$clase <- clasificar(validas$pct_60, "quantile")

mapa <- ggplot() +
  annotation_map_tile(type = "osm", zoomin = 0, alpha = 0.5) +       # mapa base OSM
  geom_sf(data = validas, aes(fill = clase), colour = NA, alpha = 0.85) +
  geom_sf(data = comunas, fill = NA, colour = "grey30", linewidth = 0.2) +
  scale_fill_brewer(palette = "YlOrRd", name = "Personas de 60+ (%)\nquintiles por manzana") +
  annotation_scale(location = "bl", width_hint = 0.25) +
  annotation_north_arrow(location = "tr", style = north_arrow_fancy_orienteering()) +
  coord_sf(crs = CRS_METROS, datum = CRS_METROS,
           xlim = gran_santiago[c("xmin", "xmax")], ylim = gran_santiago[c("ymin", "ymax")], expand = FALSE) +
  labs(title = TITULO,
       subtitle = "Porcentaje de personas de 60 años y más por manzana censal, Gran Santiago",
       caption = paste0("Fuente: INE, Censo 2024. Manzanas con menos de ", MIN_PERSONAS,
                        " personas excluidas.\nMapa base: © OpenStreetMap contributors. Proyección: UTM 19S (EPSG:32719).")) +
  theme_minimal(base_size = 10) +
  theme(plot.title = element_text(face = "bold"), legend.position = c(0.88, 0.15),
        legend.background = element_rect(fill = "white", colour = "grey80"),
        panel.grid = element_line(linetype = "dotted", colour = "grey60"))
print(mapa)
ggsave(file.path(CARPETA_SALIDA, "mapa_60mas_manzanas.png"), mapa, width = 10, height = 11, dpi = 250, bg = "white")
ggsave(file.path(CARPETA_SALIDA, "mapa_60mas_manzanas.jpg"), mapa, width = 10, height = 11, dpi = 250, bg = "white")


# Bloque 15 · Exportar a Shapefile y GeoPackage --------------------------------
salida <- comunas |> rename(pob = poblacion, pob_60mas = mayores, pct_60mas = pct_60,
                            escolarid = escolar, dens_km2 = densidad)
dir.create(file.path(CARPETA_SALIDA, "shp"), showWarnings = FALSE)
st_write(salida, file.path(CARPETA_SALIDA, "shp", "comunas_rm_60mas.shp"),
         layer_options = "ENCODING=UTF-8", append = FALSE, quiet = TRUE)
gpkg <- file.path(CARPETA_SALIDA, "censo2024_rm_60mas.gpkg")
if (file.exists(gpkg)) file.remove(gpkg)
st_write(salida, gpkg, layer = "comunas", quiet = TRUE)
st_write(validas[, c(COL_CUT, COL_COMUNA, COL_POB, COL_MAYORES, "pct_60")], gpkg, layer = "manzanas", quiet = TRUE)


# Bloque 16 · Exportar a KMZ (Google Earth) ------------------------------------
exportar_kmz <- function(capa, columna, columna_nombre, ruta, titulo, k = 5) {
  capa   <- st_transform(capa, 4326)
  cortes <- unique(classIntervals(capa[[columna]], n = k, style = "quantile")$brks)
  clase  <- cut(capa[[columna]], cortes, include.lowest = TRUE, labels = FALSE)
  colores <- grDevices::hcl.colors(length(cortes) - 1, "YlOrRd", rev = TRUE)
  kml_color <- function(hex) {            # KML usa aabbggrr
    rgb <- substring(hex, c(2, 4, 6), c(3, 5, 7)); paste0("bf", rgb[3], rgb[2], rgb[1])
  }
  anillo <- function(m) paste(sprintf("%.6f,%.6f,0", m[, 1], m[, 2]), collapse = " ")
  poligono <- function(p) {
    txt <- sprintf("<Polygon><outerBoundaryIs><LinearRing><coordinates>%s</coordinates></LinearRing></outerBoundaryIs>", anillo(p[[1]]))
    for (h in p[-1]) txt <- paste0(txt, sprintf("<innerBoundaryIs><LinearRing><coordinates>%s</coordinates></LinearRing></innerBoundaryIs>", anillo(h)))
    paste0(txt, "</Polygon>")
  }
  estilos <- paste0(sprintf('<Style id="c%d"><LineStyle><color>ffffffff</color></LineStyle><PolyStyle><color>%s</color></PolyStyle></Style>',
                            seq_along(colores), sapply(colores, kml_color)), collapse = "")
  geoms <- st_geometry(st_cast(capa, "MULTIPOLYGON"))
  marcas <- vapply(seq_len(nrow(capa)), function(i) {
    cuerpo <- paste0(vapply(geoms[[i]], poligono, ""), collapse = "")
    sprintf("<Placemark><name>%s</name><description>%s: %.1f</description><styleUrl>#c%d</styleUrl><MultiGeometry>%s</MultiGeometry></Placemark>",
            capa[[columna_nombre]][i], columna, capa[[columna]][i], clase[i], cuerpo)
  }, "")
  tmp <- tempfile(); dir.create(tmp)
  png(file.path(tmp, "leyenda.png"), width = 360, height = 60 + 40 * length(colores), res = 110)
  par(mar = c(0, 0, 0, 0)); plot.new()
  legend("topleft", fill = colores, bty = "n", title = titulo, cex = 0.9,
         legend = sprintf("%.1f – %.1f", head(cortes, -1), tail(cortes, -1)))
  dev.off()
  kml <- paste0('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
                "<name>", titulo, "</name>", estilos,
                '<ScreenOverlay><name>Leyenda</name><Icon><href>leyenda.png</href></Icon>',
                '<overlayXY x="0" y="0" xunits="fraction" yunits="fraction"/>',
                '<screenXY x="0.02" y="0.05" xunits="fraction" yunits="fraction"/></ScreenOverlay>',
                paste0(marcas, collapse = ""), "</Document></kml>")
  writeLines(enc2utf8(kml), file.path(tmp, "doc.kml"), useBytes = TRUE)
  ruta <- file.path(normalizePath(dirname(ruta)), basename(ruta))
  zip::zip(ruta, files = c("doc.kml", "leyenda.png"), root = tmp)
  message("KMZ guardado en ", ruta)
}

exportar_kmz(comunas, "pct_60", "comuna", file.path(CARPETA_SALIDA, "comunas_rm_60mas.kmz"),
             titulo = "% personas de 60+ (Censo 2024)")
