# =============================================================================
# Mapeo de variables censales en el Gran Santiago
# ¿Dónde se concentran las personas mayores (60 años y más) en el Gran Santiago?
#
# Docente: Benjamín Julio · Ingeniería Civil en Geografía, Minor en Ciencia de Datos
#          Universidad de Santiago de Chile
#
# Versión en R para RStudio: OPCIONAL y de referencia (la clase se trabaja en Google Colab).
# Homologada bloque a bloque con el notebook de Python.
# Datos: INE, Censo de Población y Vivienda 2024 — Cartografía País (GeoParquet).
#   Descarga: https://censo2024.ine.gob.cl/resultados/
#   Copia del docente: https://drive.google.com/drive/folders/1qzYq0RzuFlMieopEV03JyfpTOxxxWjij
# Ejecuta los bloques en orden. Solo debes editar el Bloque 2 (ruta del archivo).
# Si las tildes se ven mal: File > Reopen with Encoding > UTF-8.
# En RStudio, usa el panel "Outline" (Ctrl+Shift+O) para navegar entre bloques.
# =============================================================================


# Bloque 0 · Instalación de librerías -----------------------------------------
# Ejecutar solo una vez por computador (quita el # de la línea siguiente):
# install.packages(c("arrow", "sf", "dplyr", "ggplot2", "ggrepel", "ggspatial", "prettymapr",
#                    "leaflet", "htmlwidgets", "classInt", "jsonlite", "zip"))


# Bloque 1 · Cargar librerías -------------------------------------------------
library(arrow)       # leer Parquet / GeoParquet
library(sf)          # datos espaciales (simple features)
library(dplyr)       # manipulación de tablas
library(ggplot2)     # gráficos y mapas estáticos
library(ggrepel)     # etiquetas que no se superponen
library(ggspatial)   # mapa base para ggplot
library(leaflet)     # mapas web interactivos
library(htmlwidgets) # guardar el mapa web como HTML
library(classInt)    # clasificación de valores (cuantiles, etc.)


# Bloque 2 · Rutas y parámetros (EDITAR) ---------------------------------------
# Descarga la carpeta del INE (o la copia del docente) y escribe aquí la ruta del archivo de manzanas
RUTA_MANZANAS <- "C:/Users/TU_USUARIO/Descargas/Cartografia_censo2024_Pais/Cartografia_censo2024_Pais_Manzanas.parquet"
RUTA_COMUNAS  <- NULL   # opcional: ruta a Cartografia_censo2024_Pais_Comunas.parquet

CARPETA_SALIDA <- "resultados"
dir.create(CARPETA_SALIDA, showWarnings = FALSE)

COL_CUT     <- "CUT"                 # código comunal (5 dígitos)
COL_COMUNA  <- "COMUNA"
COL_POB     <- "n_per"               # total de personas
COL_MAYORES <- "n_edad_60_mas"       # personas de 60 años y más
COL_ESCOLAR <- "prom_escolaridad18"  # escolaridad promedio (18+)

# Gran Santiago: Provincia de Santiago (13101 a 13132) + Puente Alto (13201) + San Bernardo (13401)
COMUNAS_GS <- c(sprintf("131%02d", 1:32), "13201", "13401")

MIN_PERSONAS <- 20      # mínimo de personas para calcular tasas por manzana
CRS_METROS   <- 32719   # WGS 84 / UTM zona 19S
# Mapa base gris de Esri (los servidores de OpenStreetMap bloquean este tipo de uso: "Access blocked")
URL_MAPA_BASE <- "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/${z}/${y}/${x}.jpeg"
CREDITO_MAPA_BASE <- "Tiles © Esri - Esri, DeLorme, NAVTEQ"


# Bloque 3 · Explorar el archivo antes de cargarlo -----------------------------
esquema  <- open_dataset(RUTA_MANZANAS)$schema
geo_meta <- jsonlite::fromJSON(esquema$metadata$geo, simplifyVector = FALSE)
COL_GEOM <- geo_meta$primary_column
cat("Columnas:", length(esquema$names), "| geometría:", COL_GEOM, "\n")
print(grep("edad|escol", esquema$names, value = TRUE, ignore.case = TRUE))


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


# Bloque 5 · Filtrar el Gran Santiago ------------------------------------------
# Los códigos se tratan como texto para no perder ceros iniciales (ej. 05101)
manzanas[[COL_CUT]] <- sprintf("%05d", as.integer(manzanas[[COL_CUT]]))
gs <- manzanas[manzanas[[COL_CUT]] %in% COMUNAS_GS, ]
rm(manzanas); invisible(gc())
cat("Manzanas en el Gran Santiago:", nrow(gs), "| Comunas:", length(unique(gs[[COL_CUT]])), "de", length(COMUNAS_GS), "\n")


# Bloque 6 · Revisar el sistema de coordenadas ---------------------------------
print(st_crs(gs)$Name)
sf_use_s2(FALSE)
gs <- st_transform(gs, CRS_METROS)
cat("Área 1ª manzana (m²):", round(as.numeric(st_area(gs[1, ]))), "\n")


# Bloque 7 · Limpiar los datos -------------------------------------------------
for (col in c(COL_POB, COL_MAYORES, COL_ESCOLAR)) {
  x <- suppressWarnings(as.numeric(gs[[col]]))
  x[!is.na(x) & x < 0] <- NA            # valores suprimidos/negativos → faltantes
  gs[[col]] <- x
}
gs$valida <- !is.na(gs[[COL_POB]]) & gs[[COL_POB]] >= MIN_PERSONAS
cat("Manzanas válidas:", sum(gs$valida), "de", nrow(gs), "\n")


# Bloque 8 · Indicador por manzana y extensión del mapa ------------------------
gs$pct_60 <- ifelse(gs$valida, gs[[COL_MAYORES]] / gs[[COL_POB]] * 100, NA)
summary(gs$pct_60)

centros <- st_coordinates(st_centroid(st_geometry(gs[gs$valida, ])))
lim_x <- quantile(centros[, 1], c(0.005, 0.995)) + c(-1500, 1500)
lim_y <- quantile(centros[, 2], c(0.005, 0.995)) + c(-1500, 1500)


# Bloque 9 · Agregar a nivel comunal -------------------------------------------
tabla <- gs |>
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
  comunas <- gs |> group_by(cut = .data[[COL_CUT]]) |> summarise(.groups = "drop")
}

comunas <- comunas |>
  inner_join(tabla, by = "cut") |>
  mutate(densidad = poblacion / (as.numeric(st_area(geometry)) / 1e6)) |>
  st_simplify(dTolerance = 25)

comunas |> st_drop_geometry() |> arrange(desc(pct_60)) |> head(10)


# Bloque 10 · Gráfico con leyenda: envejecimiento y escolaridad ----------------
promedio_gs <- sum(comunas$mayores) / sum(comunas$poblacion) * 100
extremos <- bind_rows(slice_max(comunas, pct_60, n = 5), slice_min(comunas, pct_60, n = 5))

g <- ggplot(comunas, aes(escolar, pct_60)) +
  geom_hline(data = data.frame(y = promedio_gs, etiqueta = sprintf("Promedio Gran Santiago (%.1f%%)", promedio_gs)),
             aes(yintercept = y, linetype = etiqueta), colour = "grey50") +
  geom_point(aes(size = poblacion), colour = "#c2410c", alpha = 0.6) +
  geom_text_repel(data = extremos, aes(label = tools::toTitleCase(tolower(comuna))), size = 3,
                  min.segment.length = 0, segment.colour = "grey50", box.padding = 0.5, seed = 1) +
  scale_size_area(max_size = 12, breaks = c(1e5, 3e5, 5e5), limits = c(0, max(6e5, comunas$poblacion)),
                  labels = c("100 mil habitantes", "300 mil habitantes", "500 mil habitantes"),
                  name = "Cada burbuja es una comuna\nTamaño = población") +
  scale_linetype_manual(values = "dashed", name = NULL) +
  scale_x_continuous(expand = expansion(mult = c(0.05, 0.12))) +
  labs(title = "Gran Santiago: envejecimiento y escolaridad por comuna",
       x = "Años de escolaridad promedio (personas de 18 años y más)",
       y = "Personas de 60 años y más (%)",
       caption = "Fuente: INE, Censo de Población y Vivienda 2024.") +
  theme_minimal(base_size = 11) +
  theme(plot.title = element_text(face = "bold"), legend.position = "right")
print(g)
ggsave(file.path(CARPETA_SALIDA, "grafico_envejecimiento_escolaridad.png"), g, width = 10, height = 6.5, dpi = 200, bg = "white")


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


# Bloque 12 · Clasificación bivariada: envejecimiento y escolaridad ------------
# Paleta 3 × 3 (J. Stevens). Clave "x-y": x = % 60+, y = escolaridad (1 bajo, 3 alto)
PALETA_BI <- c("1-1" = "#e8e8e8", "2-1" = "#e4acac", "3-1" = "#c85a5a",
               "1-2" = "#b0d5df", "2-2" = "#ad9ea5", "3-2" = "#985356",
               "1-3" = "#64acbe", "2-3" = "#627f8c", "3-3" = "#574249")

clasificar_bivariado <- function(x, y) {
  paste0(ntile(x, 3), "-", ntile(y, 3))      # terciles de cada variable
}
leyenda_bivariada <- function(base_size = 9) {
  celdas <- expand.grid(x = 1:3, y = 1:3)
  celdas$color <- PALETA_BI[paste0(celdas$x, "-", celdas$y)]
  ggplot(celdas, aes(x, y, fill = color)) +
    geom_tile(colour = "white", linewidth = 0.6) +
    scale_fill_identity() + coord_equal() +
    labs(x = "% 60+ →", y = "Escolaridad →") +
    theme_void(base_size = base_size) +
    theme(axis.title.x = element_text(), axis.title.y = element_text(angle = 90),
          plot.background = element_rect(fill = "white", colour = NA))
}

bi <- gs$valida & !is.na(gs$pct_60) & !is.na(gs[[COL_ESCOLAR]])
gs$bi_clase <- NA_character_
gs$bi_clase[bi] <- clasificar_bivariado(gs$pct_60[bi], gs[[COL_ESCOLAR]][bi])
gs$bi_color <- unname(PALETA_BI[gs$bi_clase])
comunas$bi_clase <- clasificar_bivariado(comunas$pct_60, comunas$escolar)
comunas$bi_color <- unname(PALETA_BI[comunas$bi_clase])
print(leyenda_bivariada())


# Bloque 13 · Mapas interactivos (HTML) ----------------------------------------
comunas_wgs <- st_transform(comunas, 4326)
etiqueta <- ~sprintf("%s: %.1f%% de 60+, %.1f años de escolaridad", comuna, pct_60, escolar)

paleta <- colorQuantile("YlOrRd", comunas_wgs$pct_60, n = 5)
mapa_web <- leaflet(comunas_wgs) |>
  addProviderTiles("Esri.WorldGrayCanvas") |>
  addPolygons(fillColor = ~paleta(pct_60), fillOpacity = 0.75, color = "white", weight = 0.6, label = etiqueta) |>
  addLegend(pal = paleta, values = ~pct_60, title = "% 60+ (quintiles)")
saveWidget(mapa_web, file.path(normalizePath(CARPETA_SALIDA), "mapa_interactivo_60mas.html"), selfcontained = TRUE)

celdas_html <- paste0(sprintf('<div style="background:%s;width:20px;height:20px"></div>',
                              PALETA_BI[paste0(rep(1:3, 3), "-", rep(3:1, each = 3))]), collapse = "")
leyenda_html <- paste0('<b>Envejecimiento y escolaridad</b><div style="display:flex;gap:6px;margin-top:6px">',
                       '<div style="writing-mode:vertical-rl;transform:rotate(180deg)">Escolaridad →</div>',
                       '<div style="display:grid;grid-template-columns:repeat(3,20px);gap:1px">', celdas_html,
                       '</div></div><div style="margin-left:22px">% 60+ →</div>')
mapa_bi <- leaflet(comunas_wgs) |>
  addProviderTiles("Esri.WorldGrayCanvas") |>
  addPolygons(fillColor = ~bi_color, fillOpacity = 0.85, color = "white", weight = 0.6, label = etiqueta) |>
  addControl(html = leyenda_html, position = "bottomleft")
mapa_bi
saveWidget(mapa_bi, file.path(normalizePath(CARPETA_SALIDA), "mapa_interactivo_bivariado.html"), selfcontained = TRUE)


# Bloque 14-15 · Mapa profesional por manzana (PNG / JPG) ----------------------
# La leyenda, la escala y el norte van FUERA del marco del mapa (a la derecha), para no tapar manzanas.
TITULO <- "¿Dónde viven las personas mayores en el Gran Santiago?"   # reemplazar por el hallazgo
CAPTION <- paste0("Fuente: INE, Censo 2024. Manzanas con menos de ", MIN_PERSONAS, " personas excluidas.\n",
                  "Mapa base: ", CREDITO_MAPA_BASE, ". Proyección: UTM 19S (EPSG:32719).")
dx <- diff(lim_x); dy <- diff(lim_y)
ANCHO <- 12
ALTO <- 8.5 * dy / dx + 1.8

# Elementos comunes: mapa base, límites, escala de 5 km y norte a la derecha del mapa, grilla y encuadre
elementos_cartograficos <- function() {
  x0 <- lim_x[2] + 0.06 * dx; y0 <- lim_y[1] + 0.06 * dy
  list(
    annotation_map_tile(type = URL_MAPA_BASE, zoomin = 0, progress = "none"),
    geom_sf(data = comunas, fill = NA, colour = "grey30", linewidth = 0.2),
    # Escala gráfica: 4 tramos de 1,25 km
    annotate("rect", xmin = x0 + (0:3) * 1250, xmax = x0 + (1:4) * 1250, ymin = y0, ymax = y0 + 0.012 * dy,
             fill = c("black", "white", "black", "white"), colour = "black", linewidth = 0.3),
    annotate("text", x = x0 + c(0, 2500, 5000), y = y0 - 0.015 * dy, label = c("0", "2,5", "5 km"), size = 3),
    # Flecha norte
    annotate("segment", x = x0 + 2500, xend = x0 + 2500, y = y0 + 0.10 * dy, yend = y0 + 0.19 * dy,
             arrow = arrow(length = unit(0.35, "cm"), type = "closed"), linewidth = 1.2),
    annotate("text", x = x0 + 2500, y = y0 + 0.075 * dy, label = "N", fontface = "bold", size = 4.5),
    coord_sf(crs = CRS_METROS, datum = CRS_METROS, xlim = lim_x, ylim = lim_y, expand = FALSE, clip = "off"),
    theme_minimal(base_size = 10),
    theme(plot.title = element_text(face = "bold"),
          panel.grid = element_line(linetype = "dotted", colour = "grey60"),
          legend.position = "right", legend.justification = "top",
          plot.margin = margin(10, 45, 10, 10)),
    labs(x = NULL, y = NULL)
  )
}

validas <- gs[gs$valida, ]
validas$clase <- clasificar(validas$pct_60, "quantile")

mapa <- ggplot() +
  elementos_cartograficos()[1] +
  geom_sf(data = validas, aes(fill = clase), colour = NA, alpha = 0.9) +
  scale_fill_brewer(palette = "YlOrRd", name = "Personas de 60+ (%)\nquintiles por manzana") +
  elementos_cartograficos()[-1] +
  labs(title = TITULO, caption = CAPTION,
       subtitle = "Porcentaje de personas de 60 años y más por manzana censal, Gran Santiago")
print(mapa)
ggsave(file.path(CARPETA_SALIDA, "mapa_60mas_manzanas.png"), mapa, width = ANCHO, height = ALTO, dpi = 250, bg = "white")
ggsave(file.path(CARPETA_SALIDA, "mapa_60mas_manzanas.jpg"), mapa, width = ANCHO, height = ALTO, dpi = 250, bg = "white")


# Bloque 16 · Mapa bivariado profesional (PNG / JPG) ---------------------------
con_bi <- gs[!is.na(gs$bi_color), ]
lado <- 0.24 * dx                       # tamaño de la leyenda 3 × 3, a la derecha del mapa
mapa_bi_png <- ggplot() +
  elementos_cartograficos()[1] +
  geom_sf(data = con_bi, aes(fill = bi_color), colour = NA, alpha = 0.9) +
  scale_fill_identity() +
  annotation_custom(ggplotGrob(leyenda_bivariada() + labs(title = "Envejecimiento\ny escolaridad")),
                    xmin = lim_x[2] + 0.03 * dx, xmax = lim_x[2] + 0.03 * dx + lado,
                    ymin = lim_y[2] - lado * 1.25, ymax = lim_y[2]) +
  elementos_cartograficos()[-1] +
  theme(plot.margin = margin(10, 0.3 * ANCHO * 72, 10, 10)) +   # espacio a la derecha para la leyenda
  labs(title = "Envejecimiento y escolaridad en el Gran Santiago", caption = CAPTION,
       subtitle = "Terciles de % de personas de 60 años y más y de escolaridad promedio (18+) por manzana censal")
print(mapa_bi_png)
ggsave(file.path(CARPETA_SALIDA, "mapa_bivariado_manzanas.png"), mapa_bi_png, width = ANCHO, height = ALTO, dpi = 250, bg = "white")
ggsave(file.path(CARPETA_SALIDA, "mapa_bivariado_manzanas.jpg"), mapa_bi_png, width = ANCHO, height = ALTO, dpi = 250, bg = "white")


# Bloque 17 · Exportar a Shapefile y GeoPackage --------------------------------
salida <- comunas |> rename(pob = poblacion, pob_60mas = mayores, pct_60mas = pct_60,
                            escolarid = escolar, dens_km2 = densidad)
dir.create(file.path(CARPETA_SALIDA, "shp"), showWarnings = FALSE)
st_write(salida, file.path(CARPETA_SALIDA, "shp", "comunas_gran_santiago.shp"),
         layer_options = "ENCODING=UTF-8", append = FALSE, quiet = TRUE)
gpkg <- file.path(CARPETA_SALIDA, "censo2024_gran_santiago.gpkg")
if (file.exists(gpkg)) file.remove(gpkg)
st_write(salida, gpkg, layer = "comunas", quiet = TRUE)
st_write(validas[, c(COL_CUT, COL_COMUNA, COL_POB, COL_MAYORES, COL_ESCOLAR, "pct_60", "bi_clase", "bi_color")],
         gpkg, layer = "manzanas", quiet = TRUE)


# Bloque 18 · Exportar a KMZ (Google Earth) ------------------------------------
exportar_kmz <- function(capa, col_color, ruta, titulo, leyenda_png) {
  capa <- st_transform(capa, 4326)
  kml_color <- function(hex) {            # KML usa aabbggrr
    rgb <- substring(hex, c(2, 4, 6), c(3, 5, 7)); paste0("bf", rgb[3], rgb[2], rgb[1])
  }
  anillo <- function(m) paste(sprintf("%.6f,%.6f,0", m[, 1], m[, 2]), collapse = " ")
  poligono <- function(p) {
    txt <- sprintf("<Polygon><outerBoundaryIs><LinearRing><coordinates>%s</coordinates></LinearRing></outerBoundaryIs>", anillo(p[[1]]))
    for (h in p[-1]) txt <- paste0(txt, sprintf("<innerBoundaryIs><LinearRing><coordinates>%s</coordinates></LinearRing></innerBoundaryIs>", anillo(h)))
    paste0(txt, "</Polygon>")
  }
  geoms <- st_geometry(st_cast(capa, "MULTIPOLYGON"))
  marcas <- vapply(seq_len(nrow(capa)), function(i) {
    cuerpo <- paste0(vapply(geoms[[i]], poligono, ""), collapse = "")
    sprintf(paste0("<Placemark><name>%s</name><description><![CDATA[%% 60+: %.1f<br>Escolaridad: %.1f]]></description>",
                   "<Style><LineStyle><color>ffffffff</color></LineStyle><PolyStyle><color>%s</color></PolyStyle></Style>",
                   "<MultiGeometry>%s</MultiGeometry></Placemark>"),
            tools::toTitleCase(tolower(capa$comuna[i])), capa$pct_60[i], capa$escolar[i],
            kml_color(capa[[col_color]][i]), cuerpo)
  }, "")
  tmp <- tempfile(); dir.create(tmp)
  file.copy(leyenda_png, file.path(tmp, "leyenda.png"))
  kml <- paste0('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
                "<name>", titulo, "</name>",
                '<ScreenOverlay><name>Leyenda</name><Icon><href>leyenda.png</href></Icon>',
                '<overlayXY x="0" y="0" xunits="fraction" yunits="fraction"/>',
                '<screenXY x="0.02" y="0.05" xunits="fraction" yunits="fraction"/></ScreenOverlay>',
                paste0(marcas, collapse = ""), "</Document></kml>")
  writeLines(enc2utf8(kml), file.path(tmp, "doc.kml"), useBytes = TRUE)
  ruta <- file.path(normalizePath(dirname(ruta)), basename(ruta))
  zip::zip(ruta, files = c("doc.kml", "leyenda.png"), root = tmp)
  message("KMZ guardado en ", ruta)
}

# 1) Univariado: colores por quintiles de % 60+
cortes <- unique(classIntervals(comunas$pct_60, n = 5, style = "quantile")$brks)
colores <- grDevices::hcl.colors(length(cortes) - 1, "YlOrRd", rev = TRUE)
comunas$color_60 <- colores[cut(comunas$pct_60, cortes, include.lowest = TRUE, labels = FALSE)]
ley1 <- tempfile(fileext = ".png")
png(ley1, width = 360, height = 60 + 40 * length(colores), res = 110)
par(mar = c(0, 0, 0, 0)); plot.new()
legend("topleft", fill = colores, bty = "n", title = "% personas de 60+", cex = 0.9,
       legend = sprintf("%.1f – %.1f", head(cortes, -1), tail(cortes, -1)))
dev.off()
exportar_kmz(comunas, "color_60", file.path(CARPETA_SALIDA, "comunas_gs_60mas.kmz"),
             "% personas de 60+ (Censo 2024)", ley1)

# 2) Bivariado
ley2 <- tempfile(fileext = ".png")
ggsave(ley2, leyenda_bivariada(11) + labs(title = "Envejecimiento y escolaridad"), width = 2.6, height = 2.8, dpi = 150, bg = "white")
exportar_kmz(comunas, "bi_color", file.path(CARPETA_SALIDA, "comunas_gs_bivariado.kmz"),
             "Envejecimiento y escolaridad (Censo 2024)", ley2)
