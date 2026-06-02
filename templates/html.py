from __future__ import annotations


def cargar_tailwind() -> str:
    return """
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        colors: {
          kairos: {
            50: '#f4fbf7',
            100: '#dcefe4',
            200: '#b9dfca',
            300: '#87c7a1',
            400: '#58aa78',
            500: '#2E5C3E',
            600: '#244832',
            700: '#1c3625',
          },
        },
      },
    },
  }
</script>
"""


def _wrap_inner(content: str, extra_classes: str = "") -> str:
    return f"<div class='w-full {extra_classes}'>{content}</div>"


def _document(body: str) -> str:
    return f"""
    <html>
      <head>
        <meta charset="utf-8" />
        {cargar_tailwind()}
      </head>
      <body class="m-0 bg-transparent text-slate-100">
        {body}
      </body>
    </html>
    """


def render_page_hero(title: str, subtitle: str, icon_svg: str) -> str:
    return _document(_wrap_inner(
        f"""
        <section class="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-kairos-700 via-kairos-600 to-slate-900 px-8 py-10 shadow-2xl">
          <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(255,255,255,0.12),_transparent_40%)]"></div>
          <div class="relative flex flex-col items-center gap-4 text-center">
            <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 text-white ring-1 ring-white/20">
              {icon_svg}
            </div>
            <h1 class="text-4xl font-bold tracking-tight text-white md:text-5xl">{title}</h1>
            <p class="max-w-2xl text-base text-slate-100/90 md:text-lg">{subtitle}</p>
          </div>
        </section>
        """,
        "py-2",
      ))


def render_section_title(title: str, icon_svg: str = "") -> str:
    icon_html = f"<span class='mr-3 inline-flex items-center justify-center'>{icon_svg}</span>" if icon_svg else ""
    return _document(_wrap_inner(
        f"""
        <div class="mb-4 flex items-center gap-2">
          <h2 class="flex items-center text-2xl font-semibold text-slate-100">
            {icon_html}
            <span>{title}</span>
          </h2>
        </div>
        """
      ))


def render_feature_list(items: list[tuple[str, str, str]]) -> str:
    features = []
    for icon_svg, label, description in items:
        features.append(
            f"""
            <div class="group rounded-2xl border border-slate-700/70 bg-slate-900/80 p-4 shadow-lg transition hover:-translate-y-0.5 hover:border-kairos-400/70 hover:bg-slate-900">
              <div class="flex items-start gap-3">
                <div class="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-kairos-500/15 text-kairos-200 ring-1 ring-kairos-400/20">
                  {icon_svg}
                </div>
                <div class="space-y-1">
                  <div class="text-sm font-semibold text-white">{label}</div>
                  <div class="text-sm leading-6 text-slate-300">{description}</div>
                </div>
              </div>
            </div>
            """
        )

    return _document(_wrap_inner(
        f"""
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {''.join(features)}
        </div>
        """
    ))


def render_status_banner(kind: str, title: str, description: str) -> str:
    styles = {
        "success": "border-emerald-400/40 bg-emerald-500/10 text-emerald-50",
        "warning": "border-amber-400/40 bg-amber-500/10 text-amber-50",
        "info": "border-sky-400/40 bg-sky-500/10 text-sky-50",
    }
    classes = styles.get(kind, styles["info"])
    return _document(_wrap_inner(
        f"""
        <div class="rounded-2xl border px-5 py-4 shadow-lg {classes}">
          <div class="text-base font-semibold">{title}</div>
          <div class="mt-1 text-sm opacity-90">{description}</div>
        </div>
        """
      ))


def render_summary_card(label: str, value: str, caption: str = "") -> str:
    caption_html = f"<div class='mt-1 text-xs text-slate-400'>{caption}</div>" if caption else ""
    return _document(_wrap_inner(
        f"""
        <div class="rounded-2xl border border-slate-700 bg-slate-900/85 p-4 shadow-lg">
          <div class="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">{label}</div>
          <div class="mt-2 text-2xl font-semibold text-white">{value}</div>
          {caption_html}
        </div>
        """
      ))


def render_file_card(filename: str, width: int, height: int, size_kb: float, icon_svg: str) -> str:
    return _document(_wrap_inner(
        f"""
        <div class="overflow-hidden rounded-3xl border border-slate-700 bg-slate-900/90 shadow-xl">
          <div class="flex items-center gap-3 border-b border-slate-700 px-4 py-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-kairos-500/15 text-kairos-200 ring-1 ring-kairos-400/20">
              {icon_svg}
            </div>
            <div>
              <div class="text-sm font-semibold text-white">Imagen cargada</div>
              <div class="text-xs text-slate-400">{filename}</div>
            </div>
          </div>
          <div class="grid gap-3 px-4 py-4 sm:grid-cols-3">
            <div class="rounded-2xl bg-slate-800/80 px-3 py-3 text-center">
              <div class="text-xs uppercase tracking-widest text-slate-400">Ancho</div>
              <div class="mt-1 text-lg font-semibold text-white">{width}px</div>
            </div>
            <div class="rounded-2xl bg-slate-800/80 px-3 py-3 text-center">
              <div class="text-xs uppercase tracking-widest text-slate-400">Alto</div>
              <div class="mt-1 text-lg font-semibold text-white">{height}px</div>
            </div>
            <div class="rounded-2xl bg-slate-800/80 px-3 py-3 text-center">
              <div class="text-xs uppercase tracking-widest text-slate-400">Peso</div>
              <div class="mt-1 text-lg font-semibold text-white">{size_kb:.1f} KB</div>
            </div>
          </div>
        </div>
        """
      ))
