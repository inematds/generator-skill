# generator-skill

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

![Una skill, todo el flujo: /generate enruta al modelo más económico, usa referencias reales, genera imágenes o video, guarda todo en una sola carpeta y registra el prompt, el modelo y los parámetros](assets/hero-fluxo.png)

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/generator-skill/guia/es/**

Dos versiones de la skill `/generate`: un comando para que el agente genere imágenes y
videos bajo demanda, elija la ruta de menor costo, controle el gasto y guarde
todo en un solo lugar.

Son dos porque la decisión más importante de la skill —**cuál es la ruta más
barata**— tiene respuestas opuestas según la máquina.

## Cuál usar

| | [`generate-local/`](generate-local/) | [`generate-api/`](generate-api/) |
|---|---|---|
| **Para** | máquina con un modelo ejecutándose en ella | cualquier máquina, todo mediante API |
| **Ruta más barata** | local, **$0** (flux2-klein en la GPU) | modelo económico de pago, ~$0,02 |
| **Modelo de cobro** | hardware ya pagado, costo marginal cero | pago por uso en cada llamada |
| **Ruta de pago** | excepción: solo por dos motivos | es el único camino |
| **Imagen predeterminada** | flux2-klein local, ~6 s | modelo económico de imágenes |
| **Imagen con texto legible** | fal.ai, de pago (el modelo local se equivoca con las letras) | modelo de primera categoría, de pago |
| **Video predeterminado** | renderizado 2.5D local (`pixflow-motion`), $0 | modelo generativo, $0,20–0,35/s |
| **Control de costos** | existe, casi nunca se activa | se activa en cada ejecución |
| **«Haz un borrador barato y finaliza con uno caro»** | no tiene sentido: es el mismo modelo | es la regla que más ahorra |
| **Libro de cuentas** | existe, casi siempre está en cero | es el corazón de la skill |
| **Depende de** | servidor `inemaimg` en funcionamiento (puerto 8000) | `FAL_KEY` + `KIE_API_KEY` en un `.env` |
| **Límite de aviso** | $20/mes | configurable, predeterminado: $50/mes |

Lo que **no** cambia entre las dos, porque es lo que hace que el sistema perdure:
una receta Markdown por modelo, una biblioteca plana, un registro JSON junto a
cada archivo, referencias reales en lugar de descripciones y las reglas dentro
de `SKILL.md`, que el agente vuelve a leer cada vez que la usa.

## Los cinco pasos

El flujo es el mismo en las dos versiones; solo cambia el destino del paso 1.

1. **Enruta a la opción más económica** que pueda realizar la tarea y lee la receta
   de ese modelo antes de llamarlo.
2. **Usa referencias reales** —logotipos, rostros, estilo— cargadas desde `refs/`.
   Describir un logo con palabras siempre devuelve uno incorrecto.
3. **Genera** una imagen o un video. Si el modelo es asíncrono, consulta su estado y
   descárgalo de inmediato, porque la URL del resultado caduca.
4. **Guarda todo en una sola carpeta plana**, sin subcarpetas y con un nombre predecible.
5. **Registra el prompt, el modelo, los parámetros y el costo** en un JSON junto al archivo.

## Por qué un agregador y por qué pago por uso

![Se puede acceder a los modelos creativos (nano banana, kling, veo, seedance, gpt image) por dos rutas: un agregador con suscripción mensual o agregadores de pago por uso como Fal AI, Wavespeed AI y Kie AI](assets/rotas-assinatura-vs-payg.png)

Se puede acceder a los mismos modelos mediante opciones con estructuras de
cuenta muy diferentes. Las plataformas de **suscripción** cobran un monto fijo
por mes: es predecible y conveniente cuando el uso es alto y constante. Los
agregadores de **pago por uso** (fal.ai, Kie AI) cobran por llamada, con una
sola clave y una sola factura para decenas de modelos.

La versión `generate-api` asume el pago por uso por tres razones: empieza en cero,
el costo se puede atribuir a cada generación (eso es lo que alimenta el libro de
cuentas) y no se paga una mensualidad en los meses sin uso. Si el volumen aumenta
hasta el punto de que la suscripción resulte más barata, el cálculo es sencillo:
suma el mes en `--saldo` y compara.

En la versión `generate-local` no hay discusión: la GPU ya está pagada y la ruta
de pago solo se usa en las dos excepciones documentadas.

## Instalar

```bash
cp -r generate-local ~/.claude/skills/generate               # máquina con GPU
cp -r generate-api  <workspace>/.claude/skills/generate      # máquina sin modelo local
```

Ambas declaran `name: generate`. Instala **una** por workspace o cámbiale el nombre.

## Documentación

- [`generate-local/README.md`](generate-local/README.md) y
  [`generate-api/README.md`](generate-api/README.md): detalles de cada versión.
- [`doc/guia-skill-generate-ptbr.md`](doc/guia-skill-generate-ptbr.md): guía
  técnica traducida: autenticación por provider, patrón asíncrono, tabla de
  modelos y rangos de costos.
- [`doc/analise-generate-skill-guide.md`](doc/analise-generate-skill-guide.md):
  análisis del material original: qué acierta y qué faltaba (presupuesto
  acumulado, precio versionado, reanudación de un job asíncrono; los tres ya
  están implementados aquí).

## Aviso que aplica a las dos

Los IDs de modelo, los precios y los endpoints cambian con frecuencia. Todo lo
que no se haya confirmado mediante una llamada real está marcado como **NO
VERIFICADO** en las recetas. Confirma la información en la documentación actual
del provider antes de usarla en producción.
