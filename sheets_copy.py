from persistent import RunResponse
import os

def make_copy(runs: list[RunResponse]) -> str:
    return '<table style="text-align:right;"><tbody>' + "".join(run.tohtml() for run in runs) + '</tbody></table>'

def copy_html_arch(html: str):
    import subprocess
    subprocess.run(['wl-copy', '-t', 'text/html'], input=html, text=True)

def copy_html_win(html: str):
    if os.name != 'nt': raise Exception('Not the correct OS')
    import win32clipboard as winpy  # pyright: ignore[reportMissingModuleSource]
    fragment = html.encode("utf-8")

    header_template = (
        "Version:0.9\r\n"
        "StartHTML:{:010d}\r\n"
        "EndHTML:{:010d}\r\n"
        "StartFragment:{:010d}\r\n"
        "EndFragment:{:010d}\r\n"
    )

    prefix = "<html><body><!--StartFragment-->"
    suffix = "<!--EndFragment--></body></html>"

    # Offsets in CF_HTML are byte offsets from the start.
    placeholder = header_template.format(0, 0, 0, 0).encode("ascii")
    prefix_bytes = prefix.encode("utf-8")
    suffix_bytes = suffix.encode("utf-8")

    start_html = len(placeholder)
    start_fragment = start_html + len(prefix_bytes)
    end_fragment = start_fragment + len(fragment)
    end_html = end_fragment + len(suffix_bytes)

    header = header_template.format(
        start_html, end_html, start_fragment, end_fragment
    ).encode("ascii")

    payload = header + prefix_bytes + fragment + suffix_bytes

    winpy.OpenClipboard()
    try:
        winpy.EmptyClipboard()
        winpy.SetClipboardData(winpy.RegisterClipboardFormat("HTML Format"), payload)
    finally: winpy.CloseClipboard()

def copy(runs: list[RunResponse]):
    clip = make_copy(runs)
    if os.name == 'nt': copy_html_win(clip)
    else: copy_html_arch(clip)